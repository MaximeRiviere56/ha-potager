"""Fiches de culture minimales mais realistes, pour les tests."""

from __future__ import annotations

TOMATE = {
    "id": "tomate",
    "nom": "Tomate",
    "fenetres": {
        "semis_interieur": {
            "ancrage": "gelees_derniere",
            "offset_jours": -60,
            "duree_jours": 30,
        },
        "plantation": {
            "ancrage": "gelees_derniere",
            "offset_jours": 7,
            "duree_jours": 30,
        },
    },
    "cycle": {
        "jours_semis_a_repiquage": 45,
        "jours_semis_a_recolte": 110,
        "jours_plantation_a_recolte": 75,
        "duree_recolte_jours": 90,
    },
}

RADIS = {
    "id": "radis",
    "nom": "Radis",
    "fenetres": {
        "semis_direct": {
            "ancrage": "gelees_derniere",
            "offset_jours": -30,
            "duree_jours": 150,
        },
    },
    "cycle": {
        "jours_semis_a_recolte": 25,
        "duree_recolte_jours": 14,
    },
}

POMMIER = {
    "id": "pommier",
    "nom": "Pommier",
    "perenne": True,
    "fenetres": {
        "plantation": {
            "ancrage": "gelees_premiere",
            "offset_jours": 15,
            "duree_jours": 75,
        },
        "recolte": {"ancrage": "date_fixe", "date": "09-10", "duree_jours": 40},
    },
    "cycle": {"duree_recolte_jours": 40},
}
