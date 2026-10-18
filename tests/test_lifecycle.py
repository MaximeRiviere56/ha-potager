"""Le journal, ses transitions et son annulation."""

from __future__ import annotations

import unittest

from _pure import lifecycle as lc


def plante_vide() -> dict:
    return {"uid": "t1", "culture_id": "tomate", "phase": lc.PHASE_PREVU, "evenements": []}


def noter(plante: dict, type_evt: str, jour: str, **kw) -> dict:
    return lc.ajouter_evenement(plante, lc.construire_evenement(type_evt, jour, **kw))


class TestTransitions(unittest.TestCase):
    def test_semis_depuis_prevu(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07")
        self.assertEqual(p["phase"], lc.PHASE_SEME)

    def test_semer_deux_fois_refuse(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07")
        with self.assertRaises(lc.TransitionInvalide):
            noter(p, lc.EVT_SEME, "2026-03-20")

    def test_repiquer_avant_de_semer_refuse(self):
        with self.assertRaises(lc.TransitionInvalide):
            noter(plante_vide(), lc.EVT_REPIQUE, "2026-04-21")

    def test_recolte_directe_depuis_semis(self):
        """Un radis seme en place n'est jamais repique : seme -> recolte."""
        p = noter(plante_vide(), lc.EVT_SEME, "2026-04-01")
        p = noter(p, lc.EVT_RECOLTE, "2026-04-26")
        self.assertEqual(p["phase"], lc.PHASE_EN_RECOLTE)

    def test_plant_achete_depuis_prevu(self):
        p = noter(plante_vide(), lc.EVT_PLANTE, "2026-05-02")
        self.assertEqual(p["phase"], lc.PHASE_PLANTE)

    def test_type_inconnu_refuse(self):
        with self.assertRaises(lc.ErreurJournal):
            noter(plante_vide(), "arrose", "2026-05-02")

    def test_phase_finale_bloque_la_suite(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07")
        p = noter(p, lc.EVT_PERDU, "2026-03-20", cause="limaces")
        self.assertEqual(p["phase"], lc.PHASE_PERDU)
        with self.assertRaises(lc.TransitionInvalide):
            noter(p, lc.EVT_RECOLTE, "2026-07-05")


class TestRecoltes(unittest.TestCase):
    def test_recoltes_multiples_cumulees(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07")
        p = noter(p, lc.EVT_REPIQUE, "2026-04-21")
        p = noter(p, lc.EVT_RECOLTE, "2026-07-14", quantite_g=850)
        p = noter(p, lc.EVT_RECOLTE, "2026-07-21", quantite_g=1200, note="tres sucrees")
        self.assertEqual(lc.total_recolte_g(p["evenements"]), 2050)
        self.assertEqual(len(lc.recoltes(p["evenements"])), 2)

    def test_recolte_non_pesee_compte_pour_zero_mais_reste_au_journal(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-04-01")
        p = noter(p, lc.EVT_RECOLTE, "2026-04-26")
        p = noter(p, lc.EVT_RECOLTE, "2026-05-03", quantite_g=300)
        self.assertEqual(lc.total_recolte_g(p["evenements"]), 300)
        self.assertEqual(len(lc.recoltes(p["evenements"])), 2)

    def test_quantite_negative_refusee(self):
        with self.assertRaises(lc.ErreurJournal):
            lc.construire_evenement(lc.EVT_RECOLTE, "2026-07-14", quantite_g=-5)


class TestAnnulation(unittest.TestCase):
    def test_annuler_restaure_la_phase_precedente(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07")
        p = noter(p, lc.EVT_REPIQUE, "2026-04-21")
        self.assertEqual(p["phase"], lc.PHASE_PLANTE)
        retire = lc.annuler_dernier_evenement(p)
        self.assertEqual(retire["type"], lc.EVT_REPIQUE)
        self.assertEqual(p["phase"], lc.PHASE_SEME)

    def test_annuler_corrige_le_total_recolte(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-04-01")
        p = noter(p, lc.EVT_RECOLTE, "2026-04-26", quantite_g=400)
        p = noter(p, lc.EVT_RECOLTE, "2026-05-03", quantite_g=300)
        lc.annuler_dernier_evenement(p)
        self.assertEqual(lc.total_recolte_g(p["evenements"]), 400)
        self.assertEqual(p["phase"], lc.PHASE_EN_RECOLTE)

    def test_annuler_jusqu_au_vide_revient_a_prevu(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07")
        lc.annuler_dernier_evenement(p)
        self.assertEqual(p["phase"], lc.PHASE_PREVU)
        self.assertIsNone(lc.annuler_dernier_evenement(p))

    def test_la_phase_se_deduit_toujours_du_journal(self):
        """Une phase stockee incoherente ne doit pas survivre a un recalcul."""
        p = plante_vide()
        p["phase"] = lc.PHASE_EN_RECOLTE
        self.assertEqual(lc.phase_depuis_evenements(p["evenements"]), lc.PHASE_PREVU)


class TestResume(unittest.TestCase):
    def test_resume_expose_les_dates_cles(self):
        p = noter(plante_vide(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        p = noter(p, lc.EVT_REPIQUE, "2026-04-21")
        p = noter(p, lc.EVT_RECOLTE, "2026-07-14", quantite_g=850)
        r = lc.resume(p)
        self.assertEqual(r["phase"], lc.PHASE_EN_RECOLTE)
        self.assertEqual(r["date_semis"].isoformat(), "2026-03-07")
        self.assertEqual(r["date_mise_en_place"].isoformat(), "2026-04-21")
        self.assertEqual(r["mode_semis"], lc.MODE_SEMIS_INTERIEUR)
        self.assertEqual(r["total_recolte_g"], 850)


if __name__ == "__main__":
    unittest.main()
