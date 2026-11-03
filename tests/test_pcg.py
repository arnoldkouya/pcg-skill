"""Tests du script pcg.py. Lancer : python3 -m unittest discover -s tests -v"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "pcg-france"
SCRIPT = SKILL / "scripts" / "pcg.py"

spec = importlib.util.spec_from_file_location("pcg", SCRIPT)
pcg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pcg)


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = pcg.main(list(argv))
    return code, out.getvalue()


def temp_file(content, suffix=".csv", encoding="utf-8"):
    handle = tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=False)
    handle.write(content.encode(encoding))
    handle.close()
    return handle.name


FEC_HEADER = ("JournalCode\tJournalLib\tEcritureNum\tEcritureDate\tCompteNum\tCompteLib\tCompAuxNum\t"
              "CompAuxLib\tPieceRef\tPieceDate\tEcritureLib\tDebit\tCredit\tEcritureLet\tDateLet\t"
              "ValidDate\tMontantdevise\tIdevise\n")


def fec_line(journal, num, compte, debit, credit):
    return f"{journal}\tJ\t{num}\t20260101\t{compte}\tL\t\t\tP\t20260101\tLib\t{debit}\t{credit}\t\t\t20260101\t\t\n"


class PlanTests(unittest.TestCase):
    def test_plans_integrity(self):
        counts = {2023: 1025, 2024: 1025, 2025: 861, 2026: 861}
        old = {"condensed", "base", "developed"}
        new = {"minimal", "facultatif"}
        systems = {2023: old, 2024: old, 2025: new, 2026: new}
        # Particularités héritées de la source dans les plans d'avant la réforme.
        quirks = {2023: {"29187": "291", "713": "7"}, 2024: {"29187": "291", "713": "7"}}
        for year, expected in counts.items():
            plan = pcg.load_plan(SKILL / "references" / f"plan-comptable-{year}.csv")
            self.assertEqual(len(plan), expected, year)
            for code, row in plan.items():
                self.assertEqual(row["niveau"], len(code))
                self.assertEqual(str(row["classe"]), code[0])
                self.assertIn(row["systeme"], systems[year])
                self.assertIn(row["sens_usuel"], {"debit", "credit", "mixte"})
                if row["niveau"] == 1:
                    self.assertIsNone(row["parent"])
                else:
                    expected_parent = quirks.get(year, {}).get(code, code[:-1])
                    self.assertEqual(row["parent"], expected_parent, code)
                    self.assertIn(row["parent"], plan, code)

    def test_find_and_chain(self):
        code, out = run("find", "6811")
        self.assertEqual(code, 0)
        self.assertIn("6 > 68 > 681 > 6811", out)

    def test_find_unknown_returns_error(self):
        code, out = run("find", "9999")
        self.assertEqual(code, 1)
        self.assertIn("introuvable", out)

    def test_search_ignores_accents_and_case(self):
        _, out = run("search", "CLIENTS douteux")
        self.assertIn("416", out)

    def test_validate_groups(self):
        code, out = run("validate", "411", "9999", "ABC", "401000001", "--json")
        data = json.loads(out)
        self.assertEqual(data["valides"], ["411"])
        self.assertEqual(data["invalides"], ["9999"])
        self.assertEqual(data["format_incorrect"], ["ABC"])
        self.assertEqual(data["auxiliaires"], [["401000001", "401"]])
        self.assertEqual(code, 1)

    def test_tree_depth(self):
        _, out = run("tree", "44", "--depth", "1")
        self.assertIn("445", out)
        self.assertNotIn("44571", out)

    def test_year_option_and_diff(self):
        code, out = run("--annee", "2025", "stats")
        self.assertIn("Plan 2025", out)
        _, out = run("diff")
        self.assertIn("4 ajoutés, 4 supprimés, 10 modifiés", out)
        self.assertIn("1673", out)

    def test_reform_2025_accounts(self):
        plan = pcg.load_plan(SKILL / "references" / "plan-comptable-2026.csv")
        for present in ("657", "757", "747", "649", "7587"):
            self.assertIn(present, plan)
        for removed in ("79", "675", "775", "777"):
            self.assertNotIn(removed, plan)
        before = pcg.load_plan(SKILL / "references" / "plan-comptable-2024.csv")
        for existed in ("79", "675", "775", "777"):
            self.assertIn(existed, before)
        _, out = run("diff", "--de", "2024", "--vers", "2025")
        self.assertIn("71 ajoutés, 235 supprimés", out)

    def test_sens_usuel_exceptions(self):
        plan = pcg.load_plan(SKILL / "references" / "plan-comptable-2026.csv")
        expected = {"411": "debit", "419": "credit", "401": "credit", "409": "debit",
                    "281": "credit", "2813": "credit", "39": "credit", "6811": "debit",
                    "707": "credit", "709": "debit", "609": "credit", "603": "mixte",
                    "512": "mixte", "129": "debit", "120": "credit"}
        for code, sens in expected.items():
            self.assertEqual(plan[code]["sens_usuel"], sens, code)


class BalanceTests(unittest.TestCase):
    def test_example_balance(self):
        code, out = run("balance", str(ROOT / "examples" / "balance-exemple.csv"), "--json")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertTrue(data["equilibree"])
        self.assertEqual(data["resultat"], 5600.0)
        self.assertEqual(data["contre_sens"], [])
        self.assertEqual(data["codes_inconnus"], [])

    def test_unbalanced_balance_fails(self):
        path = temp_file("compte,debit,credit\n411,1000,0\n706,0,900\n")
        code, out = run("balance", path)
        self.assertEqual(code, 1)
        self.assertIn("ÉCART", out)

    def test_anomalies_detected(self):
        path = temp_file(
            "compte;debit;credit\n"
            "411;0;500,50\n"        # client créditeur
            "401;300;0\n"           # fournisseur débiteur
            "471;200;0\n"           # compte d'attente non soldé
            "9999;0;0,01\n"         # code inconnu
            "40100001;0;0\n"        # compte de l'entité rattaché au plan
            "706;0;0\n"
            "TOTAL;500;500,51\n"    # ligne de total ignorée
        )
        _, out = run("balance", path, "--json")
        data = json.loads(out)
        flagged = {item["compte"] for item in data["contre_sens"]}
        self.assertEqual(flagged, {"411", "401"})
        self.assertIn("9999", data["codes_inconnus"])
        self.assertEqual(data["auxiliaires_rattaches"], [["40100001", "401"]])
        self.assertEqual(data["comptes_attente_non_soldes"][0]["compte"], "471")
        self.assertEqual(data["lignes_ignorees"], ["TOTAL"])

    def test_label_column_before_code_column(self):
        path = temp_file("Libellé compte;Numéro de compte;Débit;Crédit\nClients;411;100;0\nVentes;706;0;100\n")
        _, out = run("balance", path, "--json")
        data = json.loads(out)
        self.assertEqual(data["comptes"], 2)
        self.assertTrue(data["equilibree"])

    def test_number_formats(self):
        parse = pcg.parse_number
        self.assertEqual(parse("1 234 567,89"), 1234567.89)
        self.assertEqual(parse("1,234,567.89"), 1234567.89)
        self.assertEqual(parse("1.234.567,89"), 1234567.89)
        self.assertEqual(parse("1234,5"), 1234.5)
        self.assertEqual(parse("(250)"), -250.0)
        self.assertEqual(parse(""), 0.0)

    def test_signed_solde_column(self):
        path = temp_file("compte,solde\n411,1000\n706,-1000\n")
        _, out = run("balance", path, "--json")
        data = json.loads(out)
        self.assertTrue(data["equilibree"])
        self.assertEqual(data["resultat"], 1000.0)


class FecTests(unittest.TestCase):
    def test_example_fec(self):
        code, out = run("fec", str(ROOT / "examples" / "fec-exemple.txt"), "--json")
        data = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(data["fec"]["ecritures"], 4)
        self.assertEqual(data["fec"]["ecritures_desequilibrees"], [])
        self.assertEqual(data["resultat"], -500.0)
        self.assertEqual(data["codes_inconnus"], [])

    def test_unbalanced_entry_detected(self):
        content = FEC_HEADER + fec_line("OD", 1, "607", "100,00", "0,00") + fec_line("OD", 1, "401", "0,00", "90,00")
        code, out = run("fec", temp_file(content, ".txt"), "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(data["fec"]["ecritures_desequilibrees"][0]["ecart"], 10.0)

    def test_pipe_separator_and_cp1252(self):
        header = FEC_HEADER.replace("\t", "|")
        lines = (fec_line("VE", 1, "411", "120,00", "0,00") + fec_line("VE", 1, "706", "0,00", "120,00")).replace("\t", "|")
        content = (header + lines).replace("Lib", "Libellé")
        code, out = run("fec", temp_file(content, ".txt", "cp1252"), "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["resultat"], 120.0)

    def test_missing_columns_exits(self):
        path = temp_file("A\tB\n1\t2\n", ".txt")
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stdout(io.StringIO()):
                pcg.main(["fec", path])


if __name__ == "__main__":
    unittest.main()
