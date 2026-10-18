"""Commandes WebSocket du panneau.

Le catalogue (108 fiches) et le journal ne passent pas par l'etat des entites :
un etat Home Assistant n'est pas fait pour transporter cela, et le ferait payer
a chaque client connecte. Le panneau interroge donc directement ces commandes.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import dt as dt_util

from . import catalog
from .const import DOMAIN, ZONE_PLEINE_TERRE
from .coordinator import PotagerCoordinator, etape_en_dict, libelle_phase
from .lifecycle import ErreurJournal, LIBELLES_EVENEMENTS, TYPES_EVENEMENTS
from .phenology import (
    ETAPE_PLANTATION,
    ETAPE_SEMIS_DIRECT,
    ETAPE_SEMIS_INTERIEUR,
    Gelees,
    fenetres_theoriques,
)


def _coordinateur(hass: HomeAssistant) -> PotagerCoordinator | None:
    entrees = hass.config_entries.async_loaded_entries(DOMAIN)
    return entrees[0].runtime_data if entrees else None


def _plante_en_dict(entree: dict, coordinator: PotagerCoordinator) -> dict[str, Any]:
    plante = entree["plante"]
    fiche = entree["culture"]
    infos = entree["resume"]
    return {
        "uid": entree["uid"],
        "culture_id": fiche["id"],
        "nom": entree["nom_affiche"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "surnom": plante.get("surnom"),
        "zone": entree["zone"],
        "notifs": plante.get("notifs", True),
        "rappel_jours": plante.get("rappel_jours"),
        "phase": infos["phase"],
        "phase_libelle": libelle_phase(infos["phase"]),
        "perenne": bool(fiche.get("perenne")),
        "prochaine": etape_en_dict(entree["prochaine"]),
        "etapes": [etape_en_dict(e) for e in entree["etapes"]],
        "date_semis": infos["date_semis"].isoformat() if infos["date_semis"] else None,
        "date_mise_en_place": (
            infos["date_mise_en_place"].isoformat()
            if infos["date_mise_en_place"]
            else None
        ),
        "nb_recoltes": infos["nb_recoltes"],
        "total_recolte_g": infos["total_recolte_g"],
        "evenements": [
            {**evt, "libelle": LIBELLES_EVENEMENTS.get(evt["type"], evt["type"])}
            for evt in plante.get("evenements") or []
        ],
        "arrosage": fiche["arrosage"],
        "exposition": fiche["exposition"],
    }


@callback
def async_enregistrer(hass: HomeAssistant) -> None:
    for commande in (
        catalogue,
        fiche_culture,
        jardin,
        ajouter,
        modifier,
        retirer,
        noter,
        annuler,
        definir_zones,
        calendrier,
    ):
        websocket_api.async_register_command(hass, commande)


# --- Lecture ------------------------------------------------------------------


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/catalogue",
        vol.Optional("requete"): str,
        vol.Optional("categorie"): str,
        vol.Optional("exposition"): str,
        vol.Optional("difficulte_max"): int,
    }
)
@callback
def catalogue(hass, connection, msg) -> None:
    resultats = catalog.rechercher(
        msg.get("requete", ""),
        categorie=msg.get("categorie"),
        exposition=msg.get("exposition"),
        difficulte_max=msg.get("difficulte_max"),
    )

    coordinator = _coordinateur(hass)
    gelees = coordinator.gelees if coordinator else Gelees()
    aujourdhui = (
        coordinator.data["calcule_le"] if coordinator else dt_util.now().date()
    )

    connection.send_result(
        msg["id"],
        {
            "cultures": [
                {**catalog.info_minimale(c), **_semis(c, gelees, aujourdhui)}
                for c in resultats
            ],
            "categories": catalog.categories(),
            "total": len(catalog.toutes()),
        },
    )


ETAPES_DE_DEPART = (ETAPE_SEMIS_INTERIEUR, ETAPE_SEMIS_DIRECT, ETAPE_PLANTATION)


def _semis(fiche: dict, gelees: Gelees, aujourdhui) -> dict[str, Any]:
    """Quand cette culture se met-elle en terre, et est-ce le moment ?

    « Qu'est-ce que je peux semer ce week-end ? » est la question la plus utile
    face a un catalogue de cent fiches : elle merite d'etre calculee ici, ou
    les dates de gelees sont connues.
    """
    candidates = [
        etape
        for annee in (aujourdhui.year, aujourdhui.year + 1)
        for etape in fenetres_theoriques(fiche, gelees, 0, annee)
        if etape.type in ETAPES_DE_DEPART and etape.fin >= aujourdhui
    ]
    if not candidates:
        return {"semable_maintenant": False, "prochain_depart": None}

    candidates.sort(key=lambda e: e.debut)
    ouverte = next((e for e in candidates if e.contient(aujourdhui)), None)
    retenue = ouverte or candidates[0]
    return {
        "semable_maintenant": ouverte is not None,
        "prochain_depart": etape_en_dict(retenue),
    }


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/culture", vol.Required("culture_id"): str}
)
@callback
def fiche_culture(hass, connection, msg) -> None:
    fiche = catalog.culture(msg["culture_id"])
    if fiche is None:
        connection.send_error(msg["id"], "introuvable", "Culture inconnue")
        return

    coordinator = _coordinateur(hass)
    gelees = coordinator.gelees if coordinator else Gelees()
    connection.send_result(
        msg["id"],
        {
            "culture": fiche,
            "compagnes": {
                cle: [catalog.info_minimale(c) for c in fiches]
                for cle, fiches in catalog.compagnes(msg["culture_id"]).items()
            },
            "fenetres": [
                etape_en_dict(e) for e in fenetres_theoriques(fiche, gelees)
            ],
        },
    )


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/jardin"})
@callback
def jardin(hass, connection, msg) -> None:
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Mon Potager n'est pas chargé")
        return

    donnees = coordinator.data
    connection.send_result(
        msg["id"],
        {
            "plantes": [
                _plante_en_dict(entree, coordinator)
                for entree in donnees["plantes"].values()
            ],
            "zones": donnees["zones"],
            "actions": [
                {
                    "uid": a["uid"],
                    "nom": a["nom"],
                    "emoji": a["emoji"],
                    "zone": a["zone"],
                    "etape": etape_en_dict(a["etape"]),
                    "jours_restants": a["jours_restants"],
                    "en_cours": a["en_cours"],
                }
                for a in donnees["actions"]
            ],
            "total_recolte_g": donnees["total_recolte_g"],
            "gelees": {
                "derniere": coordinator.gelees.derniere,
                "premiere": coordinator.gelees.premiere,
            },
            "rappel_jours": coordinator.rappel_jours,
        },
    )


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/calendrier", vol.Optional("annee"): int}
)
@callback
def calendrier(hass, connection, msg) -> None:
    """Bandes annuelles par plante, prevues et reelles, pour la vue calendrier."""
    coordinator = _coordinateur(hass)
    if coordinator is None:
        connection.send_error(msg["id"], "non_charge", "Mon Potager n'est pas chargé")
        return

    annee = msg.get("annee") or coordinator.data["calcule_le"].year
    lignes = []
    for entree in coordinator.data["plantes"].values():
        decalage = coordinator.store.decalage_zone(entree["plante"].get("zone"))
        lignes.append(
            {
                "uid": entree["uid"],
                "nom": entree["nom_affiche"],
                "emoji": entree["culture"]["emoji"],
                "zone": entree["zone"]["nom"],
                "prevues": [
                    etape_en_dict(e)
                    for e in fenetres_theoriques(
                        entree["culture"], coordinator.gelees, decalage, annee
                    )
                ],
                "reelles": [etape_en_dict(e) for e in entree["etapes"] if e.reelle],
                "evenements": [
                    evt
                    for evt in entree["plante"].get("evenements") or []
                    if evt["date"][:4] == str(annee)
                ],
            }
        )
    connection.send_result(msg["id"], {"annee": annee, "lignes": lignes})


# --- Ecriture -----------------------------------------------------------------


def _avec_coordinateur(fonction):
    """Resout le coordinateur, remonte proprement les refus du journal."""

    async def enveloppe(hass, connection, msg) -> None:
        coordinator = _coordinateur(hass)
        if coordinator is None:
            connection.send_error(
                msg["id"], "non_charge", "Mon Potager n'est pas chargé"
            )
            return
        try:
            resultat = await fonction(coordinator, msg)
        except ErreurJournal as err:
            # Transition refusee ou plante disparue : c'est une erreur d'usage,
            # elle a sa place dans l'interface, pas dans les logs.
            connection.send_error(msg["id"], "refuse", str(err))
            return
        connection.send_result(msg["id"], resultat or {"ok": True})

    enveloppe.__name__ = fonction.__name__
    return enveloppe


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/ajouter",
        vol.Required("culture_id"): str,
        vol.Optional("zone", default=ZONE_PLEINE_TERRE): str,
        vol.Optional("surnom"): vol.Any(str, None),
        vol.Optional("notifs", default=True): bool,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def ajouter(coordinator, msg) -> dict:
    if catalog.culture(msg["culture_id"]) is None:
        raise ErreurJournal(f"Culture inconnue : {msg['culture_id']}")
    plante = await coordinator.async_appliquer(
        lambda: coordinator.store.ajouter_plante(
            msg["culture_id"],
            zone=msg["zone"],
            surnom=msg.get("surnom"),
            notifs=msg["notifs"],
        )
    )
    return {"uid": plante["uid"]}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/modifier",
        vol.Required("uid"): str,
        vol.Optional("zone"): str,
        vol.Optional("surnom"): vol.Any(str, None),
        vol.Optional("notifs"): bool,
        vol.Optional("rappel_jours"): vol.Any(int, None),
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def modifier(coordinator, msg) -> dict:
    champs = {
        cle: msg[cle]
        for cle in ("zone", "surnom", "notifs", "rappel_jours")
        if cle in msg
    }
    await coordinator.async_appliquer(
        lambda: coordinator.store.modifier_plante(msg["uid"], **champs)
    )
    return {"ok": True}


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/retirer", vol.Required("uid"): str}
)
@websocket_api.async_response
@_avec_coordinateur
async def retirer(coordinator, msg) -> dict:
    await coordinator.async_appliquer(
        lambda: coordinator.store.retirer_plante(msg["uid"])
    )
    return {"ok": True}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/noter",
        vol.Required("uid"): str,
        vol.Required("evenement"): vol.In(sorted(TYPES_EVENEMENTS)),
        vol.Optional("date"): vol.Any(str, None),
        vol.Optional("mode"): str,
        vol.Optional("quantite_g"): vol.Any(int, None),
        vol.Optional("cause"): str,
        vol.Optional("note"): str,
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def noter(coordinator, msg) -> dict:
    jour = msg.get("date") or coordinator.data["calcule_le"]
    details = {
        cle: msg[cle]
        for cle in ("mode", "quantite_g", "cause", "note")
        if msg.get(cle) is not None
    }
    plante = await coordinator.async_appliquer(
        lambda: coordinator.store.noter(msg["uid"], msg["evenement"], jour, **details)
    )
    return {"phase": plante["phase"]}


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/annuler", vol.Required("uid"): str}
)
@websocket_api.async_response
@_avec_coordinateur
async def annuler(coordinator, msg) -> dict:
    retire = await coordinator.async_appliquer(
        lambda: coordinator.store.annuler(msg["uid"])
    )
    return {"retire": retire}


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/zones",
        vol.Required("zones"): [
            {
                vol.Required("id"): str,
                vol.Required("nom"): str,
                vol.Required("decalage_jours"): int,
            }
        ],
    }
)
@websocket_api.async_response
@_avec_coordinateur
async def definir_zones(coordinator, msg) -> dict:
    await coordinator.async_appliquer(
        lambda: coordinator.store.definir_zones(msg["zones"])
    )
    return {"ok": True}
