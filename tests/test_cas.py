"""Cas de test avec soldes de clôture connus.

Chaque dossier de examples/cas/ contient une balance avant clôture (avant.csv),
les écritures de clôture (ecritures.csv) et les résultats attendus (attendu.json),
calculés à la main. Ce test vérifie deux choses :
1. les chiffres attendus sont cohérents entre eux (recalcul indépendant du script) ;
2. le script retrouve les mêmes totaux et le même résultat.
"""
import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAS = ROOT / "examples" / "cas"
SCRIPT = ROOT / "skills" / "pcg-france" / "scripts" / "pcg.py"
CONTRE = ("28", "29", "39", "49", "59")


def lire(path):
    with open(path, encoding="utf-8", newline="") as f:
        return [(r["compte"], float(r["debit"] or 0), float(r["credit"] or 0)) for r in csv.DictReader(f)]


def soldes(*fichiers):
    out = {}
    for fichier in fichiers:
        for compte, debit, credit in lire(fichier):
            out[compte] = out.get(compte, 0.0) + debit - credit
    return out


class CasDeTest(unittest.TestCase):
    def test_il_y_a_des_cas(self):
        self.assertGreaterEqual(len(list(CAS.glob("*/attendu.json"))), 2)

    def test_chaque_cas(self):
        for dossier in sorted(p.parent for p in CAS.glob("*/attendu.json")):
            with self.subTest(cas=dossier.name):
                attendu = json.loads((dossier / "attendu.json").read_text(encoding="utf-8"))
                avant, ecr = dossier / "avant.csv", dossier / "ecritures.csv"

                # 1. Recalcul indépendant
                for fichier in (avant, ecr):
                    lignes = lire(fichier)
                    self.assertAlmostEqual(sum(d for _, d, _ in lignes), sum(c for _, _, c in lignes), places=2)
                s = soldes(avant, ecr)
                charges = sum(v for c, v in s.items() if c[0] == "6")
                produits = -sum(v for c, v in s.items() if c[0] == "7")
                net8 = -sum(v for c, v in s.items() if c[0] == "8")
                resultat = produits + net8 - charges
                actif = sum(v for c, v in s.items() if c[0] in "12345" and (v > 0 or c.startswith(CONTRE)))
                passif = -sum(v for c, v in s.items()
                              if c[0] in "12345" and v < 0 and not c.startswith(CONTRE)) + resultat
                self.assertAlmostEqual(resultat, attendu["resultat"], places=2)
                self.assertAlmostEqual(actif, attendu["total_actif_net"], places=2)
                self.assertAlmostEqual(passif, attendu["total_passif_avec_resultat"], places=2)
                self.assertAlmostEqual(actif, passif, places=2)
                self.assertEqual({c: v for c, v in s.items() if abs(v) > 0.005},
                                 {c: float(v) for c, v in attendu["soldes_apres"].items()})

                # 2. Le script donne les mêmes chiffres
                proc = subprocess.run(
                    [sys.executable, "-I", str(SCRIPT), "balance", str(avant), "--ecritures", str(ecr), "--json"],
                    capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                rapport = json.loads(proc.stdout)
                self.assertTrue(rapport["equilibree"])
                self.assertEqual(rapport["codes_inconnus"], [])
                self.assertAlmostEqual(rapport["total_debit"], attendu["total_debit_apres"], places=2)
                self.assertAlmostEqual(rapport["total_credit"], attendu["total_credit_apres"], places=2)
                self.assertAlmostEqual(rapport["resultat"], attendu["resultat"], places=2)
                self.assertAlmostEqual(rapport["charges_classe6"], attendu["charges_classe6"], places=2)
                self.assertAlmostEqual(rapport["produits_classe7"], attendu["produits_classe7"], places=2)

    def test_balance_avant_cloture_seule_n_a_pas_le_meme_resultat(self):
        # Garde-fou : sans les écritures, le résultat provisoire diffère du résultat final.
        for dossier in sorted(p.parent for p in CAS.glob("*/attendu.json")):
            attendu = json.loads((dossier / "attendu.json").read_text(encoding="utf-8"))
            proc = subprocess.run([sys.executable, "-I", str(SCRIPT), "balance", str(dossier / "avant.csv"), "--json"],
                                  capture_output=True, text=True, encoding="utf-8")
            self.assertNotAlmostEqual(json.loads(proc.stdout)["resultat"], attendu["resultat"], places=2)


if __name__ == "__main__":
    unittest.main()
