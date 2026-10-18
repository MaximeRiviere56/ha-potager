"""Coordinateur : agrege jardin, catalogue et moteur en une vue unique.

Il n'y a rien a interroger sur le reseau : tout est calcule localement. Le
DataUpdateCoordinator sert ici pour sa plomberie (abonnement des entites,
rafraichissement sur demande) et pour un recalcul horaire, qui suffit a faire
basculer les etapes au passage de minuit.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import date, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import catalog
from .const import (
    CONF_GELEES_DERNIERE,
    CONF_GELEES_PREMIERE,
    CONF_RAPPEL_JOURS,
    DEFAUT_GELEES_DERNIERE,
    DEFAUT_GELEES_PREMIERE,
    DEFAUT_RAPPEL_JOURS,
    DOMAIN,
)
from .lifecycle import PHASES_LIBELLES, resume as resume_journal
from .phenology import Gelees, prochaines_etapes
from .store import JardinStore

_LOGGER = logging.getLogger(__name__)

INTERVALLE = timedelta(hours=1)


class PotagerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Vue calculee du potager, partagee par toutes les entites."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, store: JardinStore
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=INTERVALLE,
            config_entry=entry,
        )
        self.entry = entry
        self.store = store

    # --- Options -------------------------------------------------------------

    @property
    def gelees(self) -> Gelees:
        options = self.entry.options
        return Gelees(
            derniere=options.get(CONF_GELEES_DERNIERE, DEFAUT_GELEES_DERNIERE),
            premiere=options.get(CONF_GELEES_PREMIERE, DEFAUT_GELEES_PREMIERE),
        )

    @property
    def rappel_jours(self) -> int:
        return int(self.entry.options.get(CONF_RAPPEL_JOURS, DEFAUT_RAPPEL_JOURS))

    def rappel_pour(self, plante: dict) -> int:
        """Le reglage de la plante prime sur le reglage global."""
        propre = plante.get("rappel_jours")
        return int(propre) if propre is not None else self.rappel_jours

    # --- Calcul --------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        return await self.hass.async_add_executor_job(self._calculer)

    def _calculer(self) -> dict[str, Any]:
        aujourdhui = date.today()
        gelees = self.gelees
        plantes: dict[str, dict] = {}
        actions: list[dict] = []
        total_recolte = 0

        for brute in self.store.plantes:
            uid = brute["uid"]
            fiche = catalog.culture(brute["culture_id"])
            if fiche is None:
                _LOGGER.warning(
                    "Culture absente du catalogue, plante ignoree : %s",
                    brute["culture_id"],
                )
                continue

            decalage = self.store.decalage_zone(brute.get("zone"))
            etapes = prochaines_etapes(fiche, brute, gelees, decalage, aujourdhui)
            infos = resume_journal(brute)
            total_recolte += infos["total_recolte_g"]

            entree = {
                "uid": uid,
                "plante": brute,
                "culture": fiche,
                "zone": self.store.zone(brute.get("zone")),
                "etapes": etapes,
                "prochaine": etapes[0] if etapes else None,
                "resume": infos,
                "nom_affiche": nom_affiche(brute, fiche),
            }
            plantes[uid] = entree

            prochaine = entree["prochaine"]
            if prochaine is not None:
                restants = prochaine.jours_restants(aujourdhui)
                if restants <= self.rappel_pour(brute):
                    actions.append(
                        {
                            "uid": uid,
                            "nom": entree["nom_affiche"],
                            "emoji": fiche["emoji"],
                            "zone": entree["zone"]["nom"],
                            "etape": prochaine,
                            "jours_restants": restants,
                            "en_cours": prochaine.contient(aujourdhui),
                        }
                    )

        actions.sort(key=lambda a: (a["etape"].debut, a["nom"]))

        return {
            "plantes": plantes,
            "zones": list(self.store.zones),
            "actions": actions,
            "total_recolte_g": total_recolte,
            "calcule_le": aujourdhui,
        }

    # --- Ecriture : toute mutation passe par un rafraichissement -------------

    async def async_appliquer(self, mutation) -> Any:
        """Execute une mutation du store puis recalcule la vue.

        Point de passage unique : aucun appelant n'a a se souvenir de
        rafraichir, donc entites et panneau ne peuvent pas rester en retard.
        """
        resultat = mutation()
        # `async_refresh` et non `async_request_refresh` : ce dernier est
        # debounce, et le panneau qui rappelle `potager/jardin` juste apres
        # recevrait l'etat d'avant la mutation. Le calcul etant pur et local,
        # il n'y a rien a economiser en le differant.
        await self.async_refresh()
        return resultat


def nom_affiche(plante: dict, fiche: dict) -> str:
    surnom = plante.get("surnom")
    return f"{fiche['nom']} ({surnom})" if surnom else fiche["nom"]


def etape_en_dict(etape) -> dict | None:
    """Serialise une etape pour le panneau et les attributs d'entite."""
    if etape is None:
        return None
    donnees = asdict(etape)
    donnees["debut"] = etape.debut.isoformat()
    donnees["fin"] = etape.fin.isoformat()
    donnees["libelle"] = etape.libelle
    donnees["reelle"] = etape.reelle
    return donnees


def libelle_phase(phase: str) -> str:
    return PHASES_LIBELLES.get(phase, phase)
