"""Fiches de culture minimales mais realistes, pour les tests."""

from __future__ import annotations

TOMATE = {
    "id": "tomate",
    "nom": "Tomate",
    "rusticite": {"gel": False, "temp_min_c": 5},
    "arrosage": {"besoin": "eleve", "frequence_jours": 2, "notes": ""},
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
    "rusticite": {"gel": True, "temp_min_c": -4},
    "arrosage": {"besoin": "eleve", "frequence_jours": 2, "notes": ""},
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
    "rusticite": {"gel": True, "temp_min_c": -25},
    "arrosage": {"besoin": "faible", "frequence_jours": 10, "notes": ""},
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
