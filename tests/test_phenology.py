"""Le moteur d'etapes : ancrage climatique, zones, et priorite du reel."""

from __future__ import annotations

import unittest
from datetime import date

from _pure import lifecycle as lc
from _pure import phenology as ph
from fixtures import POMMIER, RADIS, TOMATE

GELEES = ph.Gelees(derniere="04-15", premiere="11-15")


def plante(culture_id: str = "tomate", **kw) -> dict:
    base = {"uid": "t1", "culture_id": culture_id, "phase": lc.PHASE_PREVU, "evenements": []}
    base.update(kw)
    return base


def noter(p: dict, type_evt: str, jour: str, **kw) -> dict:
    return lc.ajouter_evenement(p, lc.construire_evenement(type_evt, jour, **kw))


def par_type(etapes) -> dict:
    return {e.type: e for e in etapes}


class TestAncrageClimatique(unittest.TestCase):
    def test_fenetres_ancrees_sur_la_derniere_gelee(self):
        etapes = par_type(ph.fenetres_theoriques(TOMATE, GELEES, 0, 2026))
        # 15 avril - 60 j
        self.assertEqual(etapes["semis_interieur"].debut, date(2026, 2, 14))
        # 15 avril + 7 j
        self.assertEqual(etapes["plantation"].debut, date(2026, 4, 22))

    def test_recolte_deduite_de_la_plantation(self):
        etapes = par_type(ph.fenetres_theoriques(TOMATE, GELEES, 0, 2026))
        self.assertEqual(
            etapes["recolte"].debut,
            etapes["plantation"].debut + __import__("datetime").timedelta(days=75),
        )

    def test_gelees_differentes_decalent_tout(self):
        montagne = ph.Gelees(derniere="05-20", premiere="10-05")
        ici = par_type(ph.fenetres_theoriques(TOMATE, GELEES, 0, 2026))
        la_bas = par_type(ph.fenetres_theoriques(TOMATE, montagne, 0, 2026))
        ecart = (la_bas["plantation"].debut - ici["plantation"].debut).days
        self.assertEqual(ecart, 35)

    def test_date_fixe_pour_une_perenne(self):
        etapes = par_type(ph.fenetres_theoriques(POMMIER, GELEES, 0, 2026))
        self.assertEqual(etapes["recolte"].debut, date(2026, 9, 10))

    def test_29_fevrier_tolere_en_annee_commune(self):
        culture = {
            "fenetres": {"semis_direct": {"ancrage": "date_fixe", "date": "02-29"}},
            "cycle": {},
        }
        etapes = ph.fenetres_theoriques(culture, GELEES, 0, 2027)
        self.assertEqual(etapes[0].debut, date(2027, 2, 28))

    def test_ancrage_inconnu_rejete(self):
        culture = {"fenetres": {"semis_direct": {"ancrage": "pleine_lune"}}, "cycle": {}}
        with self.assertRaises(ph.CatalogueInvalide):
            ph.fenetres_theoriques(culture, GELEES, 0, 2026)


class TestZones(unittest.TestCase):
    def test_la_serre_prend_de_l_avance(self):
        pleine_terre = par_type(ph.fenetres_theoriques(TOMATE, GELEES, 0, 2026))
        serre = par_type(ph.fenetres_theoriques(TOMATE, GELEES, -21, 2026))
        self.assertEqual(
            (pleine_terre["plantation"].debut - serre["plantation"].debut).days, 21
        )

    def test_la_zone_ne_decale_jamais_une_date_reelle(self):
        """Une date au journal est un fait : la zone n'a rien a y redire."""
        p = noter(plante(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        sans = ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 3, 8))
        avec = ph.prochaines_etapes(TOMATE, p, GELEES, -21, date(2026, 3, 8))
        self.assertEqual([e.debut for e in sans], [e.debut for e in avec])


class TestLeReelGagne(unittest.TestCase):
    def test_semer_en_retard_decale_la_recolte_d_autant(self):
        tot = noter(plante(), lc.EVT_SEME, "2026-02-14", mode=lc.MODE_SEMIS_INTERIEUR)
        tard = noter(plante(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        r_tot = par_type(ph.prochaines_etapes(TOMATE, tot, GELEES, 0, date(2026, 2, 15)))
        r_tard = par_type(ph.prochaines_etapes(TOMATE, tard, GELEES, 0, date(2026, 3, 8)))
        self.assertEqual((r_tard["recolte"].debut - r_tot["recolte"].debut).days, 21)
        self.assertEqual((r_tard["repiquage"].debut - r_tot["repiquage"].debut).days, 21)

    def test_la_chaine_part_du_semis_reel(self):
        p = noter(plante(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        etapes = par_type(ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 3, 8)))
        self.assertEqual(etapes["repiquage"].debut, date(2026, 4, 21))  # +45 j
        self.assertEqual(etapes["recolte"].debut, date(2026, 7, 5))  # +75 j
        self.assertTrue(all(e.reelle for e in etapes.values()))

    def test_repiquage_reel_recalcule_la_recolte(self):
        p = noter(plante(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        p = noter(p, lc.EVT_REPIQUE, "2026-05-10")  # 19 j plus tard que prevu
        etapes = par_type(ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 5, 11)))
        self.assertEqual(etapes["recolte"].debut, date(2026, 7, 24))  # 10 mai + 75 j
        self.assertNotIn("repiquage", etapes)

    def test_semis_en_place_va_droit_a_la_recolte(self):
        p = noter(plante("radis"), lc.EVT_SEME, "2026-04-01", mode=lc.MODE_SEMIS_DIRECT)
        etapes = ph.prochaines_etapes(RADIS, p, GELEES, 0, date(2026, 4, 2))
        self.assertEqual([e.type for e in etapes], ["recolte"])
        self.assertEqual(etapes[0].debut, date(2026, 4, 26))  # +25 j

    def test_plant_achete_part_de_sa_plantation(self):
        p = noter(plante(), lc.EVT_PLANTE, "2026-05-02")
        etapes = ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 5, 3))
        self.assertEqual(etapes[0].type, "recolte")
        self.assertEqual(etapes[0].debut, date(2026, 7, 16))  # +75 j

    def test_recolte_en_cours_court_depuis_la_premiere_reelle(self):
        p = noter(plante(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        p = noter(p, lc.EVT_REPIQUE, "2026-04-21")
        p = noter(p, lc.EVT_RECOLTE, "2026-07-14", quantite_g=850)
        etapes = ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 8, 1))
        self.assertEqual(etapes[0].debut, date(2026, 7, 14))
        self.assertEqual(etapes[0].fin, date(2026, 10, 12))  # +90 j
        self.assertTrue(etapes[0].contient(date(2026, 8, 1)))


class TestFinDeVie(unittest.TestCase):
    def test_une_plante_perdue_n_a_plus_d_etape(self):
        p = noter(plante(), lc.EVT_SEME, "2026-03-07")
        p = noter(p, lc.EVT_PERDU, "2026-03-20", cause="limaces")
        self.assertEqual(ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 4, 1)), [])

    def test_une_plante_terminee_n_a_plus_d_etape(self):
        p = noter(plante(), lc.EVT_PLANTE, "2026-05-02")
        p = noter(p, lc.EVT_TERMINE, "2026-10-30")
        self.assertEqual(ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 11, 1)), [])

    def test_recolte_achevee_ne_reste_pas_affichee(self):
        p = noter(plante(), lc.EVT_SEME, "2026-03-07", mode=lc.MODE_SEMIS_INTERIEUR)
        p = noter(p, lc.EVT_REPIQUE, "2026-04-21")
        p = noter(p, lc.EVT_RECOLTE, "2026-07-14")
        self.assertEqual(
            ph.prochaines_etapes(TOMATE, p, GELEES, 0, date(2026, 11, 1)), []
        )


class TestPerennes(unittest.TestCase):
    def test_un_pommier_plante_ne_se_resseme_pas(self):
        p = noter(plante("pommier"), lc.EVT_PLANTE, "2025-12-01")
        etapes = ph.prochaines_etapes(POMMIER, p, GELEES, 0, date(2026, 3, 1))
        self.assertEqual({e.type for e in etapes}, {"recolte"})
        self.assertEqual(etapes[0].debut, date(2026, 9, 10))

    def test_la_recolte_d_une_perenne_revient_chaque_annee(self):
        p = noter(plante("pommier"), lc.EVT_PLANTE, "2025-12-01")
        etapes = ph.prochaines_etapes(POMMIER, p, GELEES, 0, date(2026, 3, 1))
        annees = sorted({e.debut.year for e in etapes})
        self.assertEqual(annees, [2026, 2027])

    def test_une_recolte_notee_ne_coupe_pas_les_annees_suivantes(self):
        p = noter(plante("pommier"), lc.EVT_PLANTE, "2025-12-01")
        p = noter(p, lc.EVT_RECOLTE, "2026-09-15", quantite_g=12000)
        # Mi-octobre la fenetre 2026 court toujours : on cueille encore.
        encore = ph.prochaines_etapes(POMMIER, p, GELEES, 0, date(2026, 10, 1))
        self.assertEqual(encore[0].debut, date(2026, 9, 10))
        # Une fois la fenetre refermee, c'est celle de l'an prochain qui vient.
        apres = ph.prochaines_etapes(POMMIER, p, GELEES, 0, date(2026, 11, 1))
        self.assertTrue(apres)
        self.assertEqual(apres[0].debut, date(2027, 9, 10))


class TestBasculeDAnnee(unittest.TestCase):
    def test_en_decembre_on_voit_l_annee_suivante(self):
        """Sans cela, un potager consulte en decembre serait vide."""
        etapes = ph.prochaines_etapes(TOMATE, plante(), GELEES, 0, date(2026, 12, 20))
        self.assertTrue(etapes)
        self.assertEqual(etapes[0].debut, date(2027, 2, 14))
        self.assertEqual(etapes[0].type, "semis_interieur")

    def test_les_fenetres_fermees_sont_ecartees(self):
        """Au 1er juin, le semis de fevrier est passe : il ne reste que la
        recolte en cours, puis la saison suivante."""
        aujourdhui = date(2026, 6, 1)
        etapes = ph.prochaines_etapes(TOMATE, plante(), GELEES, 0, aujourdhui)
        self.assertTrue(all(e.fin >= aujourdhui for e in etapes))
        self.assertEqual(etapes[0].type, "recolte")
        self.assertEqual(etapes[0].debut.year, 2026)
        # Le prochain semis propose est bien celui de l'annee suivante.
        semis = [e for e in etapes if e.type == "semis_interieur"]
        self.assertEqual([e.debut.year for e in semis], [2027])

    def test_les_etapes_sont_triees_par_urgence(self):
        etapes = ph.prochaines_etapes(TOMATE, plante(), GELEES, 0, date(2026, 1, 1))
        self.assertEqual([e.debut for e in etapes], sorted(e.debut for e in etapes))
        self.assertEqual(etapes[0].type, "semis_interieur")


class TestProchaineEtape(unittest.TestCase):
    def test_jours_restants_negatifs_si_fenetre_ouverte(self):
        etape = ph.prochaine_etape(TOMATE, plante(), GELEES, 0, date(2026, 2, 20))
        self.assertEqual(etape.type, "semis_interieur")
        self.assertEqual(etape.jours_restants(date(2026, 2, 20)), -6)

    def test_aucune_etape_pour_une_plante_perdue(self):
        p = noter(plante(), lc.EVT_SEME, "2026-03-07")
        p = noter(p, lc.EVT_PERDU, "2026-03-20")
        self.assertIsNone(ph.prochaine_etape(TOMATE, p, GELEES, 0, date(2026, 4, 1)))


if __name__ == "__main__":
    unittest.main()
