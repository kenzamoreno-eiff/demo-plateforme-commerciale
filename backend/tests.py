"""Tests du moteur.  Lancement : python backend/tests.py"""

import copy
import sys
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

import actions  # noqa: E402
import db  # noqa: E402
import moteur  # noqa: E402

SEED = db.lire_seed(ICI.parent / "frontend" / "seed.js")
CTX = {"aujourdhui": "2026-11-01", "maintenant": "2026-11-01 10:00", "seed": SEED}


class TestRegles(unittest.TestCase):
    def test_endress_hauser_cinq_opportunites(self):
        ex = SEED["exemplePrediag"]
        regles = moteur.evaluer(SEED["regles"], ex["valeurs"], ["IRVE", "GTB"], "2026-11-01", "prediag")
        self.assertEqual([r["id"] for r in regles], ["R03", "R05", "R07", "R09", "R10"])

    def test_audit_recent_ne_declenche_pas(self):
        v = {"consoElec": "3", "auditDate": "2024-01-01"}
        ids = [r["id"] for r in moteur.evaluer(SEED["regles"], v, [], "2026-11-01", "prediag")]
        self.assertNotIn("R01", ids)
        v["auditDate"] = "2021-01-01"
        ids = [r["id"] for r in moteur.evaluer(SEED["regles"], v, [], "2026-11-01", "prediag")]
        self.assertIn("R01", ids)

    def test_vente_complementaire(self):
        ids = [r["id"] for r in moteur.evaluer(SEED["regles"], {}, ["PV", "Batteries"], "2026-11-01", "parc")]
        self.assertEqual(ids, ["R11"])
        ids = [r["id"] for r in moteur.evaluer(SEED["regles"], {}, ["PV", "Batteries", "EMS"], "2026-11-01", "parc")]
        self.assertEqual(ids, [])


class TestCalculette(unittest.TestCase):
    params = {"margeDefaut": 20, "prixMWhCumac": 8.5}

    def test_exemple_du_draft(self):
        # devis 152 k€, aides 100 k€ -> reste à charge 52 k€
        produits = [{"id": "X", "prixAchat": 152000 / 1.2}]
        aides = [{"id": "F", "nom": "Aide", "type": "fixe", "coefKwhc": 0}]
        ch = {"lignes": [{"produitId": "X", "qte": 1}], "mainOeuvre": 0, "marge": 20, "base": "avant",
              "aides": [{"aideId": "F", "montant": 100000}]}
        r = moteur.calculer(ch, produits, aides, self.params)
        self.assertEqual(r["pv"], 152000)
        self.assertEqual(r["rac"], 52000)
        self.assertAlmostEqual(r["marge"], 25333.33, places=2)

    def test_marge_apres_aides(self):
        produits = [{"id": "X", "prixAchat": 1000}]
        aides = [{"id": "F", "nom": "Aide", "type": "fixe", "coefKwhc": 0}]
        ch = {"lignes": [{"produitId": "X", "qte": 1}], "mainOeuvre": 0, "marge": 20, "base": "apres",
              "aides": [{"aideId": "F", "montant": 400}]}
        r = moteur.calculer(ch, produits, aides, self.params)
        self.assertEqual(r["rac"], 720)   # (1000 - 400) x 1,2
        self.assertEqual(r["marge"], 120)

    def test_cee(self):
        a = {"id": "C", "nom": "CEE", "type": "cee", "coefKwhc": 600}
        self.assertEqual(moteur.montant_aide(a, {"qte": 9000}, 8.5), {"kwhc": 5400000, "montant": 45900})

    def test_alertes(self):
        produits = [{"id": "X", "prixAchat": 1000}]
        aides = [{"id": "F", "nom": "Aide", "type": "fixe", "coefKwhc": 0}]
        ch = {"lignes": [{"produitId": "X", "qte": 1}], "mainOeuvre": 0, "marge": 20, "base": "avant",
              "aides": [{"aideId": "F", "montant": 1500}]}
        niveaux = [a["niveau"] for a in moteur.calculer(ch, produits, aides, self.params)["alertes"]]
        self.assertEqual(niveaux, ["critique", "attention"])


class TestActions(unittest.TestCase):
    def setUp(self):
        self.st = actions.etat_initial(SEED)

    def test_parcours_complet(self):
        ex = copy.deepcopy(SEED["exemplePrediag"])
        r = actions.enregistrer_prediag(self.st, ex, CTX)
        self.assertEqual(len(r["crees"]), 5)
        # relancer le même pré-diagnostic ne crée pas de doublon
        self.assertEqual(actions.enregistrer_prediag(self.st, ex, CTX)["crees"], [])
        opp = r["crees"][0]
        actions.statut_opportunite(self.st, {"id": opp, "statut": "Validée"}, CTX)
        aff = actions.creer_affaire(self.st, {"oppId": opp}, CTX)["affaireId"]
        self.assertEqual(aff, "AFF-2026-004")
        actions.changer_etape(self.st, {"id": aff, "etape": "B"}, CTX)
        a = next(a for a in self.st["affaires"] if a["id"] == aff)
        self.assertIn("Bureau d'études automatisme", [i["service"] for i in a["interlocuteurs"]])

    def test_import_csv(self):
        csv_txt = "nom;site;lat;lon;statut\nSite test;Mulhouse;47,75;7,33;client\n;vide;;;\n"
        self.assertEqual(actions.importer_clients(self.st, {"csv": csv_txt}, CTX)["importes"], 1)
        c = self.st["clients"][-1]
        self.assertEqual((c["lat"], c["statut"]), (47.75, "Client"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
