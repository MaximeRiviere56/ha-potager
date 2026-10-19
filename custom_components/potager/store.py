"""Persistance du jardin : plantes, journal, zones.

Le journal est la seule source de verite sur l'etat d'une plante ; la phase
stockee n'est qu'un cache recalcule a chaque ecriture. Toute mutation passe
par ce module, qui valide via `lifecycle` avant d'ecrire.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION, ZONE_PLEINE_TERRE, ZONES_DEFAUT
from .lifecycle import (
    ErreurJournal,
    PHASE_PREVU,
    ajouter_evenement,
    annuler_dernier_evenement,
    construire_evenement,
    phase_depuis_evenements,
)

_LOGGER = logging.getLogger(__name__)


class PlanteInconnue(ErreurJournal):
    """Aucune plante du jardin ne porte cet identifiant."""


class JardinStore:
    """Enveloppe typee autour du Store de Home Assistant."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._donnees: dict[str, Any] = {
            "plantes": [],
            "zones": [],
            "cultures_perso": [],
        }

    # --- Cycle de vie du stockage --------------------------------------------

    async def async_charger(self) -> None:
        charge = await self._store.async_load()
        if charge:
            self._donnees = charge
        self._donnees.setdefault("plantes", [])
        self._donnees.setdefault("cultures_perso", [])
        if not self._donnees.get("zones"):
            self._donnees["zones"] = [dict(z) for z in ZONES_DEFAUT]
        # Les phases sont recalculees au chargement : un journal edite a la main
        # ou une version anterieure du schema se remet ainsi d'aplomb.
        for plante in self._donnees["plantes"]:
            plante["phase"] = phase_depuis_evenements(plante.get("evenements") or [])

    def _sauvegarder(self) -> None:
        """Programme une ecriture au prochain tour de boucle.

        Delai zero, et non quelques secondes : le jardin pese quelques kilo-
        octets, il n'y a rien a gagner a differer, et une fenetre d'attente est
        une fenetre pendant laquelle un arret de Home Assistant perd des
        donnees. Les mutations utilisateur passent de toute facon par
        `async_sauvegarder_maintenant`, qui attend l'ecriture.
        """
        self._store.async_delay_save(lambda: self._donnees, 0)

    async def async_sauvegarder_maintenant(self) -> None:
        """Ecrit sur disque et attend que ce soit fait."""
        await self._store.async_save(self._donnees)

    # --- Lecture -------------------------------------------------------------

    @property
    def plantes(self) -> list[dict]:
        return self._donnees["plantes"]

    @property
    def zones(self) -> list[dict]:
        return self._donnees["zones"]

    def plante(self, uid: str) -> dict:
        for plante in self.plantes:
            if plante["uid"] == uid:
                return plante
        raise PlanteInconnue(f"Plante introuvable dans le jardin : {uid}")

    def zone(self, zone_id: str | None) -> dict:
        for zone in self.zones:
            if zone["id"] == zone_id:
                return zone
        return {"id": ZONE_PLEINE_TERRE, "nom": "Pleine terre", "decalage_jours": 0}

    def decalage_zone(self, zone_id: str | None) -> int:
        return int(self.zone(zone_id).get("decalage_jours", 0))

    # --- Ecriture : plantes --------------------------------------------------

    def ajouter_plante(
        self,
        culture_id: str,
        *,
        zone: str = ZONE_PLEINE_TERRE,
        surnom: str | None = None,
        notifs: bool = True,
        rappel_jours: int | None = None,
    ) -> dict:
        """Une culture peut etre ajoutee plusieurs fois : deux semis echelonnes,
        ou le meme legume en serre et en pleine terre. D'ou l'uid."""
        plante = {
            "uid": uuid.uuid4().hex[:8],
            "culture_id": culture_id,
            "zone": zone,
            "surnom": surnom or None,
            "phase": PHASE_PREVU,
            "notifs": notifs,
            "rappel_jours": rappel_jours,
            "evenements": [],
        }
        self.plantes.append(plante)
        self._sauvegarder()
        return plante

    def retirer_plante(self, uid: str) -> dict:
        plante = self.plante(uid)
        self.plantes.remove(plante)
        self.purger_notifs(uid)
        self._sauvegarder()
        return plante

    def modifier_plante(self, uid: str, **champs: Any) -> dict:
        """Modifie les reglages d'une plante. Le journal n'est pas touchable ici."""
        plante = self.plante(uid)
        for cle in ("zone", "surnom", "notifs", "rappel_jours"):
            if cle in champs:
                plante[cle] = champs[cle]
        self._sauvegarder()
        return plante

    # --- Ecriture : journal --------------------------------------------------

    def noter(self, uid: str, type_evt: str, jour: Any, **details: Any) -> dict:
        """Ajoute un evenement au journal apres validation de la transition."""
        plante = self.plante(uid)
        evt = construire_evenement(type_evt, jour, **details)
        ajouter_evenement(plante, evt)
        self._sauvegarder()
        return plante

    def annuler(self, uid: str) -> dict | None:
        plante = self.plante(uid)
        retire = annuler_dernier_evenement(plante)
        if retire is not None:
            self._sauvegarder()
        return retire

    # --- Catalogue personnel -------------------------------------------------
    #
    # Les fiches saisies par l'utilisateur vivent ici, et non dans le fichier
    # livre avec l'integration : une mise a jour ne doit jamais les effacer.

    @property
    def cultures_perso(self) -> list[dict]:
        return self._donnees.setdefault("cultures_perso", [])

    def enregistrer_culture(self, fiche: dict) -> dict:
        """Cree ou remplace une fiche personnelle, selon son id."""
        cultures = self.cultures_perso
        for index, existante in enumerate(cultures):
            if existante["id"] == fiche["id"]:
                cultures[index] = fiche
                break
        else:
            cultures.append(fiche)
        self._sauvegarder()
        return fiche

    def supprimer_culture(self, culture_id: str) -> None:
        """Refuse tant qu'une plante du jardin s'appuie sur cette fiche :
        sans elle, la plante deviendrait un orphelin silencieux."""
        utilisees = [p for p in self.plantes if p["culture_id"] == culture_id]
        if utilisees:
            noms = ", ".join(p.get("surnom") or p["culture_id"] for p in utilisees)
            raise ErreurJournal(
                f"Cette fiche est utilisée par {len(utilisees)} plante(s) du "
                f"jardin ({noms}). Retirez-les d'abord."
            )
        self._donnees["cultures_perso"] = [
            c for c in self.cultures_perso if c["id"] != culture_id
        ]
        self._sauvegarder()

    # --- Etat des rappels ----------------------------------------------------
    #
    # Memoriser ce qui a deja ete envoye est ce qui separe un rappel utile d'un
    # harcelement quotidien : une fenetre de semis reste ouverte un mois.

    @property
    def etat_notifs(self) -> dict[str, Any]:
        return self._donnees.setdefault("notifs", {"envoyees": {}, "reports": {}})

    def notif_deja_envoyee(self, cle: str) -> bool:
        return cle in self.etat_notifs["envoyees"]

    def dernier_envoi(self, cle: str) -> str | None:
        """Date du dernier rappel envoye pour cette occurrence, ou None.

        La date, et non un simple booleen : une relance de recolte doit savoir
        depuis combien de jours le dernier message est parti.
        """
        return self.etat_notifs["envoyees"].get(cle)

    def marquer_notif_envoyee(self, cle: str, jour: str) -> None:
        self.etat_notifs["envoyees"][cle] = jour
        self._sauvegarder()

    def reporter(self, cle: str, jusqu_au: str) -> None:
        self.etat_notifs["reports"][cle] = jusqu_au
        self._sauvegarder()

    def report_en_cours(self, cle: str, aujourdhui: str) -> bool:
        jusqu_au = self.etat_notifs["reports"].get(cle)
        return bool(jusqu_au and jusqu_au > aujourdhui)

    def purger_notifs(self, uid: str) -> None:
        """Au retrait d'une plante, ne pas laisser son etat de rappel derriere."""
        for bloc in ("envoyees", "reports"):
            table = self.etat_notifs[bloc]
            for cle in [c for c in table if c.startswith(f"{uid}:")]:
                del table[cle]

    # --- Ecriture : zones ----------------------------------------------------

    def definir_zones(self, zones: list[dict]) -> None:
        """Les plantes rattachees a une zone disparue retombent en pleine terre."""
        self._donnees["zones"] = zones
        connues = {zone["id"] for zone in zones}
        for plante in self.plantes:
            if plante.get("zone") not in connues:
                plante["zone"] = ZONE_PLEINE_TERRE
        self._sauvegarder()
