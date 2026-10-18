"""Integrite du catalogue, et son passage dans le moteur.

Le test croise est le plus utile du lot : il fait passer les 108 fiches dans
`prochaines_etapes` a plusieurs dates de l'annee. Une fiche mal remplie ne
casse pas a l'ecriture, elle casse six mois plus tard chez l'utilisateur.
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest
from datetime import date

from _pure import lifecycle as lc
from _pure import phenology as ph

RACINE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "tools"))

from build_catalog import valider  # noqa: E402
from catalogue_source import CULTURES  # noqa: E402

CATALOG_JSON = RACINE / "custom_components" / "potager" / "data" / "catalog.json"
GELEES = ph.Gelees(derniere="04-15", premiere="11-15")

# Quelques dates reparties sur l'annee, dont les deux pieges : le creux de
# l'hiver et la fin decembre, ou il faut deja voir la saison suivante.
DATES_SONDE = [
    date(2026, 1, 15),
    date(2026, 3, 1),
    date(2026, 5, 20),
    date(2026, 8, 10),
    date(2026, 10, 5),
    date(2026, 12, 28),
]


class TestIntegrite(unittest.TestCase):
    def test_catalogue_sans_probleme(self):
        problemes = valider(CULTURES)
        self.assertEqual(problemes, [], "\n".join(problemes))

    def test_json_a_jour(self):
        """Le JSON livre doit correspondre a la table source."""
        self.assertTrue(CATALOG_JSON.exists(), "lancer tools/build_catalog.py")
        charge = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
        self.assertEqual(len(charge["cultures"]), len(CULTURES))
        self.assertEqual(
            {c["id"] for c in charge["cultures"]}, {c["id"] for c in CULTURES}
        )

    def test_taille_annoncee(self):
        self.assertGreaterEqual(len(CULTURES), 100)

    def test_associations_symetriques_quand_elles_existent(self):
        """Si A evite B, B ne doit pas aimer A : ce serait un conseil contradictoire."""
        par_id = {c["id"]: c for c in CULTURES}
        for c in CULTURES:
            for evite in c["associations"]["evite"]:
                autre = par_id[evite]
                self.assertNotIn(
                    c["id"],
                    autre["associations"]["aime"],
                    f"{c['id']} evite {evite}, mais {evite} aime {c['id']}",
                )


class TestCatalogueDansLeMoteur(unittest.TestCase):
    def test_toute_culture_produit_des_etapes_toute_l_annee(self):
        for culture in CULTURES:
            plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
            for jour in DATES_SONDE:
                with self.subTest(culture=culture["id"], jour=jour):
                    etapes = ph.prochaines_etapes(culture, plante, GELEES, 0, jour)
                    self.assertTrue(
                        etapes,
                        f"{culture['id']} n'a aucune etape a venir au {jour}",
                    )

    def test_toute_culture_sait_mener_un_cycle_complet(self):
        """Semer, puis mettre en place, doit rester calculable partout."""
        for culture in CULTURES:
            if culture.get("perenne"):
                continue
            fenetres = culture["fenetres"]
            interieur = "semis_interieur" in fenetres
            plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
            with self.subTest(culture=culture["id"]):
                if interieur or "semis_direct" in fenetres:
                    lc.ajouter_evenement(
                        plante,
                        lc.construire_evenement(
                            lc.EVT_SEME,
                            "2026-04-01",
                            mode=lc.MODE_SEMIS_INTERIEUR if interieur else lc.MODE_SEMIS_DIRECT,
                        ),
                    )
                else:
                    lc.ajouter_evenement(
                        plante, lc.construire_evenement(lc.EVT_PLANTE, "2026-04-01")
                    )
                etapes = ph.prochaines_etapes(
                    culture, plante, GELEES, 0, date(2026, 4, 2)
                )
                self.assertTrue(etapes, f"{culture['id']} : chaine interrompue")
                self.assertTrue(
                    any(e.type == ph.ETAPE_RECOLTE for e in etapes),
                    f"{culture['id']} : aucune recolte calculee apres mise en place",
                )

    def test_les_perennes_ne_demandent_jamais_de_semis(self):
        for culture in CULTURES:
            if not culture.get("perenne"):
                continue
            plante = {"uid": "x", "culture_id": culture["id"], "evenements": []}
            lc.ajouter_evenement(
                plante, lc.construire_evenement(lc.EVT_PLANTE, "2025-11-20")
            )
            etapes = ph.prochaines_etapes(culture, plante, GELEES, 0, date(2026, 3, 1))
            with self.subTest(culture=culture["id"]):
                self.assertEqual({e.type for e in etapes}, {ph.ETAPE_RECOLTE})


if __name__ == "__main__":
    unittest.main()
