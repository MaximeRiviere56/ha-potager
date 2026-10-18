#!/usr/bin/env python3
"""Genere tools/fixture.js pour le banc d'essai du panneau.

Les reponses simulees sortent du vrai catalogue et du vrai moteur : le banc
verifie donc le panneau face aux donnees qu'il recevra reellement, et non face
a un jeu d'essai ecrit a la main qui finirait par mentir.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import types
from datetime import date, timedelta

RACINE = pathlib.Path(__file__).resolve().parent.parent
SRC = RACINE / "custom_components" / "potager"

_pkg = types.ModuleType("potager_banc")
_pkg.__path__ = [str(SRC)]
sys.modules["potager_banc"] = _pkg


def _charger(nom: str):
    spec = importlib.util.spec_from_file_location(f"potager_banc.{nom}", SRC / f"{nom}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"potager_banc.{nom}"] = module
    spec.loader.exec_module(module)
    return module


lc = _charger("lifecycle")
ph = _charger("phenology")
cat = _charger("catalog")

GELEES = ph.Gelees("04-15", "11-15")
AUJ = date.today()
DEPARTS = ("semis_interieur", "semis_direct", "plantation")

ZONES = [
    {"id": "pleine-terre", "nom": "Pleine terre", "decalage_jours": 0},
    {"id": "serre", "nom": "Serre", "decalage_jours": -21},
    {"id": "chassis", "nom": "Chassis / tunnel", "decalage_jours": -10},
    {"id": "balcon", "nom": "Balcon / pots", "decalage_jours": 0},
]


def etape_dict(etape) -> dict:
    return {
        "type": etape.type,
        "debut": etape.debut.isoformat(),
        "fin": etape.fin.isoformat(),
        "source": etape.source,
        "libelle": etape.libelle,
        "reelle": etape.reelle,
    }


def construire(culture_id, zone_id, evenements, surnom=None) -> dict:
    fiche = cat.culture(culture_id)
    zone = next(z for z in ZONES if z["id"] == zone_id)
    plante = {
        "uid": culture_id[:6],
        "culture_id": culture_id,
        "evenements": [],
        "surnom": surnom,
        "notifs": True,
        "rappel_jours": None,
        "zone": zone_id,
    }
    for type_evt, jour, extra in evenements:
        lc.ajouter_evenement(plante, lc.construire_evenement(type_evt, jour, **extra))

    etapes = ph.prochaines_etapes(fiche, plante, GELEES, zone["decalage_jours"], AUJ)
    infos = lc.resume(plante)
    return {
        "uid": plante["uid"],
        "culture_id": culture_id,
        "nom": f"{fiche['nom']} ({surnom})" if surnom else fiche["nom"],
        "emoji": fiche["emoji"],
        "categorie": fiche["categorie"],
        "surnom": surnom,
        "zone": zone,
        "notifs": True,
        "rappel_jours": None,
        "phase": infos["phase"],
        "phase_libelle": lc.PHASES_LIBELLES[infos["phase"]],
        "perenne": bool(fiche.get("perenne")),
        "prochaine": etape_dict(etapes[0]) if etapes else None,
        "etapes": [etape_dict(e) for e in etapes],
        "date_semis": infos["date_semis"].isoformat() if infos["date_semis"] else None,
        "date_mise_en_place": (
            infos["date_mise_en_place"].isoformat() if infos["date_mise_en_place"] else None
        ),
        "nb_recoltes": infos["nb_recoltes"],
        "total_recolte_g": infos["total_recolte_g"],
        "evenements": [
            {**e, "libelle": lc.LIBELLES_EVENEMENTS[e["type"]]} for e in plante["evenements"]
        ],
        "arrosage": fiche["arrosage"],
        "exposition": fiche["exposition"],
    }


def depart(fiche) -> dict:
    candidates = [
        e
        for annee in (AUJ.year, AUJ.year + 1)
        for e in ph.fenetres_theoriques(fiche, GELEES, 0, annee)
        if e.type in DEPARTS and e.fin >= AUJ
    ]
    if not candidates:
        return {"semable_maintenant": False, "prochain_depart": None}
    candidates.sort(key=lambda e: e.debut)
    ouverte = next((e for e in candidates if e.contient(AUJ)), None)
    return {
        "semable_maintenant": ouverte is not None,
        "prochain_depart": etape_dict(ouverte or candidates[0]),
    }


def main() -> None:
    il_y_a = lambda n: (AUJ - timedelta(days=n)).isoformat()  # noqa: E731

    # Un echantillon qui couvre les cinq phases : c'est la seule facon de voir
    # si une vue se casse sur un cas de bord.
    plantes = [
        construire("tomate", "serre", [("seme", il_y_a(40), {"mode": "interieur"})], "Cœur de bœuf"),
        construire("radis", "pleine-terre", []),
        construire(
            "courgette",
            "pleine-terre",
            [
                ("plante", il_y_a(70), {}),
                ("recolte", il_y_a(9), {"quantite_g": 620}),
                ("recolte", il_y_a(2), {"quantite_g": 840, "note": "trois belles"}),
            ],
        ),
        construire("pommier", "pleine-terre", [("plante", "2024-11-20", {})]),
        construire(
            "laitue",
            "balcon",
            [("seme", il_y_a(60), {"mode": "direct"}), ("perdu", il_y_a(30), {"cause": "limaces"})],
        ),
    ]

    actions = []
    for plante in plantes:
        prochaine = plante["prochaine"]
        if not prochaine:
            continue
        debut = date.fromisoformat(prochaine["debut"])
        fin = date.fromisoformat(prochaine["fin"])
        restants = (debut - AUJ).days
        if restants <= 3:
            actions.append(
                {
                    "uid": plante["uid"],
                    "nom": plante["nom"],
                    "emoji": plante["emoji"],
                    "zone": plante["zone"]["nom"],
                    "etape": prochaine,
                    "jours_restants": restants,
                    "en_cours": debut <= AUJ <= fin,
                }
            )

    jardin = {
        "plantes": plantes,
        "zones": ZONES,
        "actions": actions,
        "total_recolte_g": sum(p["total_recolte_g"] for p in plantes),
        "gelees": {"derniere": GELEES.derniere, "premiere": GELEES.premiere},
        "rappel_jours": 3,
    }
    catalogue = {
        "cultures": [{**cat.info_minimale(c), **depart(c)} for c in cat.toutes()],
        "categories": cat.categories(),
        "total": len(cat.toutes()),
    }
    tomate = cat.culture("tomate")
    fiche = {
        "culture": tomate,
        "compagnes": {
            cle: [cat.info_minimale(x) for x in valeur]
            for cle, valeur in cat.compagnes("tomate").items()
        },
        "fenetres": [etape_dict(e) for e in ph.fenetres_theoriques(tomate, GELEES)],
    }

    sortie = RACINE / "tools" / "fixture.js"
    sortie.write_text(
        "// Genere par tools/banc_fixture.py — ne pas editer a la main.\n"
        "window.__hassFactice = {\n  states: {},\n  callWS: async (msg) => {\n"
        "    const reponses = {\n"
        f'      "potager/jardin": {json.dumps(jardin, ensure_ascii=False)},\n'
        f'      "potager/catalogue": {json.dumps(catalogue, ensure_ascii=False)},\n'
        f'      "potager/culture": {json.dumps(fiche, ensure_ascii=False)},\n'
        "    };\n"
        '    if (!(msg.type in reponses)) throw new Error("commande non simulee : " + msg.type);\n'
        "    return reponses[msg.type];\n  },\n};\n",
        encoding="utf-8",
    )
    print(f"{sortie.relative_to(RACINE)} : {len(plantes)} plantes, {len(actions)} actions")
    for plante in plantes:
        prochaine = plante["prochaine"] or {}
        print(
            f"  {plante['nom']:28} {plante['phase_libelle']:11} "
            f"{prochaine.get('libelle', '—')} {prochaine.get('debut', '')}"
        )


if __name__ == "__main__":
    main()
