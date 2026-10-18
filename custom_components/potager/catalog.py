"""Chargement et interrogation du catalogue de cultures."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

CHEMIN_CATALOGUE = Path(__file__).parent / "data" / "catalog.json"


@lru_cache(maxsize=1)
def charger() -> dict[str, dict]:
    """Catalogue indexe par id. Lu une seule fois, le fichier est fige."""
    try:
        charge = json.loads(CHEMIN_CATALOGUE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _LOGGER.exception("Catalogue illisible : %s", CHEMIN_CATALOGUE)
        return {}
    return {culture["id"]: culture for culture in charge.get("cultures", [])}


def culture(culture_id: str) -> dict | None:
    return charger().get(culture_id)


def toutes() -> list[dict]:
    return sorted(charger().values(), key=lambda c: c["nom"])


def categories() -> list[str]:
    return sorted({c["categorie"] for c in charger().values()})


def familles() -> list[str]:
    return sorted({c["famille"] for c in charger().values()})


def _sans_accents(texte: str) -> str:
    """Pour que 'poireau' trouve 'Poirée' et que 'oeillet' trouve 'Œillet'."""
    remplacements = str.maketrans(
        "àâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ", "aaaeeeeiioouuuycAAAEEEEIIOOUUUYC"
    )
    return texte.translate(remplacements).replace("œ", "oe").replace("Œ", "OE").lower()


def rechercher(
    requete: str = "",
    *,
    categorie: str | None = None,
    exposition: str | None = None,
    difficulte_max: int | None = None,
    perenne: bool | None = None,
) -> list[dict]:
    """Recherche texte libre et filtres, cumulables."""
    resultats = toutes()

    if requete:
        terme = _sans_accents(requete.strip())
        resultats = [
            c
            for c in resultats
            if terme in _sans_accents(c["nom"])
            or terme in _sans_accents(c["nom_scientifique"])
            or terme in _sans_accents(c["famille"])
        ]
    if categorie:
        resultats = [c for c in resultats if c["categorie"] == categorie]
    if exposition:
        resultats = [c for c in resultats if c["exposition"] == exposition]
    if difficulte_max is not None:
        resultats = [c for c in resultats if c["difficulte"] <= difficulte_max]
    if perenne is not None:
        resultats = [c for c in resultats if bool(c.get("perenne")) is perenne]

    return resultats


def compagnes(culture_id: str) -> dict[str, list[dict]]:
    """Fiches completes des compagnes, pour l'affichage de la fiche."""
    fiche = culture(culture_id)
    if not fiche:
        return {"aime": [], "evite": []}
    index = charger()
    return {
        cle: [index[autre] for autre in fiche["associations"][cle] if autre in index]
        for cle in ("aime", "evite")
    }


def info_minimale(fiche: dict) -> dict[str, Any]:
    """Version allegee d'une fiche, pour les listes du panneau."""
    return {
        "id": fiche["id"],
        "nom": fiche["nom"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "famille": fiche["famille"],
        "difficulte": fiche["difficulte"],
        "exposition": fiche["exposition"],
        "perenne": bool(fiche.get("perenne")),
        "arrosage": fiche["arrosage"],
    }
