#!/usr/bin/env python3
"""Outil en ligne de commande pour le Plan comptable général (PCG) français.

Bibliothèque standard uniquement (Python 3.8+).

Commandes : find, search, validate, tree, classe, export, stats, diff,
balance, fec. Le plan est lu dans references/plan-comptable-AAAA.csv (année
choisie avec --annee, 2026 par défaut). Chemin modifiable avec --plan ou la
variable d'environnement PCG_PLAN.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

TOL = 0.005
MAX_PLAN_DIGITS = 5
DEFAULT_YEAR = 2026
COLUMNS = ["code", "libelle", "classe", "niveau", "parent", "systeme", "nature", "sens_usuel"]


# --------------------------------------------------------------------------
# Chargement du plan
# --------------------------------------------------------------------------

def plan_path(year: int, explicit: str | None) -> Path:
    here = Path(__file__).resolve().parent
    name = f"plan-comptable-{year}.csv"
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("PCG_PLAN"):
        candidates.append(Path(os.environ["PCG_PLAN"]))
    candidates += [here.parent / "references" / name, here / name, Path.cwd() / name]
    for path in candidates:
        if path.is_file():
            return path
    sys.exit(f"Fichier {name} introuvable. Utiliser --plan CHEMIN ou --annee.")


def load_plan(path: Path) -> dict[str, dict]:
    plan: dict[str, dict] = {}
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            row["classe"] = int(row["classe"])
            row["niveau"] = int(row["niveau"])
            row["parent"] = row["parent"] or None
            plan[row["code"]] = row
    return plan


def norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.lower().replace("’", "'")


def resolve(code: str, plan: dict[str, dict]):
    """Retourne (compte, exact). Cherche le plus long préfixe existant."""
    if code in plan:
        return plan[code], True
    for size in range(min(len(code), MAX_PLAN_DIGITS), 0, -1):
        if code[:size] in plan:
            return plan[code[:size]], False
    return None, False


def chain(code: str, plan: dict[str, dict]) -> list[dict]:
    out = []
    current = plan.get(code)
    while current:
        out.append(current)
        current = plan.get(current["parent"]) if current["parent"] else None
    return list(reversed(out))


def children(code: str, plan: dict[str, dict]) -> list[dict]:
    return [r for r in plan.values() if r["parent"] == code]


def suggestions(code: str, plan: dict[str, dict], limit: int = 6) -> list[dict]:
    """Comptes voisins : même préfixe le plus long."""
    for size in range(min(len(code), 4), 0, -1):
        prefix = code[:size]
        found = [r for c, r in plan.items() if c.startswith(prefix) and c != code]
        if found:
            return found[:limit]
    return []


def line(row: dict) -> str:
    return f"{row['code']:<6} {row['libelle']}  [{row['systeme']}, {row['sens_usuel']}]"


# --------------------------------------------------------------------------
# Commandes sur le plan
# --------------------------------------------------------------------------

def cmd_find(args, plan):
    code = args.code.strip()
    row = plan.get(code)
    if not row:
        print(f"Compte {code} introuvable dans le plan {args.annee}.")
        near = suggestions(code, plan)
        if near:
            print("Comptes voisins :")
            for r in near:
                print("  " + line(r))
        return 1
    print(f"{row['code']} : {row['libelle']}")
    print(f"  Classe {row['classe']}, niveau {row['niveau']}, nature {row['nature']}, "
          f"système {row['systeme']}, sens usuel (indicatif) {row['sens_usuel']}")
    print("  Chemin : " + " > ".join(r["code"] for r in chain(code, plan)))
    kids = children(code, plan)
    if kids:
        print("  Enfants :")
        for r in kids:
            print("    " + line(r))
    return 0


def cmd_search(args, plan):
    words = norm(args.terme).split()
    hits = []
    for row in plan.values():
        if args.classe and row["classe"] != args.classe:
            continue
        haystack = row["code"] + " " + norm(row["libelle"])
        if all(w in haystack for w in words):
            hits.append(row)
    for row in hits[: args.limit]:
        print(line(row))
    if len(hits) > args.limit:
        print(f"... {len(hits) - args.limit} autres résultats (utiliser --limit).")
    if not hits:
        print("Aucun résultat.")
        return 1
    return 0


def cmd_validate(args, plan):
    codes = list(args.codes)
    if codes == ["-"]:
        codes = sys.stdin.read().split()
    result = {"valides": [], "invalides": [], "format_incorrect": [], "auxiliaires": []}
    for code in codes:
        if not re.fullmatch(r"\d+", code):
            result["format_incorrect"].append(code)
        elif len(code) > MAX_PLAN_DIGITS:
            parent, _ = resolve(code, plan)
            result["auxiliaires"].append((code, parent["code"] if parent else None))
        elif code in plan:
            result["valides"].append(code)
        else:
            result["invalides"].append(code)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Valides ({len(result['valides'])}) : {' '.join(result['valides']) or '-'}")
        print(f"Invalides ({len(result['invalides'])}) :")
        for code in result["invalides"]:
            near = ", ".join(r["code"] for r in suggestions(code, plan, 4)) or "aucun"
            print(f"  {code}  (voisins : {near})")
        print(f"Format incorrect ({len(result['format_incorrect'])}) : {' '.join(result['format_incorrect']) or '-'}")
        if result["auxiliaires"]:
            print(f"Codes de plus de {MAX_PLAN_DIGITS} chiffres (comptes de l'entité, rattachés au plan) :")
            for code, parent in result["auxiliaires"]:
                print(f"  {code} -> {parent or 'aucun préfixe connu'}")
    return 1 if result["invalides"] or result["format_incorrect"] else 0


def cmd_tree(args, plan):
    root = plan.get(args.code)
    if not root:
        print(f"Compte {args.code} introuvable.")
        return 1

    def walk(row, depth):
        print("  " * depth + line(row))
        if args.depth is None or depth < args.depth:
            for child in children(row["code"], plan):
                walk(child, depth + 1)

    walk(root, 0)
    return 0


def select(plan, classe=None, niveau=None, nature=None, sens=None, systeme=None):
    return [
        r for r in plan.values()
        if (classe is None or r["classe"] == classe)
        and (niveau is None or r["niveau"] == niveau)
        and (nature is None or r["nature"] == nature)
        and (sens is None or r["sens_usuel"] == sens)
        and (systeme is None or r["systeme"] == systeme)
    ]


def cmd_classe(args, plan):
    for row in select(plan, classe=args.numero, niveau=args.niveau):
        print(line(row))
    return 0


def cmd_export(args, plan):
    rows = select(plan, args.classe, args.niveau, args.nature, args.sens, args.systeme)
    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    elif args.format == "md":
        print("| Code | Libellé | Système | Sens usuel |\n|---|---|---|---|")
        for r in rows:
            print(f"| {r['code']} | {r['libelle']} | {r['systeme']} | {r['sens_usuel']} |")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("" if r[k] is None else r[k]) for k in COLUMNS})
    return 0


def cmd_stats(args, plan):
    print(f"Plan {args.annee} : {len(plan)} comptes")
    for classe in range(1, 9):
        print(f"  Classe {classe} : {len(select(plan, classe=classe))}")
    counts = {}
    for row in plan.values():
        counts[row["systeme"]] = counts.get(row["systeme"], 0) + 1
    print("  Systèmes : " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


def cmd_diff(args, plan):
    old = load_plan(plan_path(args.de, None))
    new = load_plan(plan_path(args.vers, None))
    added = [new[c] for c in new if c not in old]
    removed = [old[c] for c in old if c not in new]
    modified = [(old[c], new[c]) for c in new if c in old
                and (old[c]["libelle"] != new[c]["libelle"] or old[c]["systeme"] != new[c]["systeme"])]
    print(f"Plan {args.de} -> {args.vers} : {len(added)} ajoutés, {len(removed)} supprimés, {len(modified)} modifiés")
    print("\nAjoutés :")
    for r in added:
        print("  + " + line(r))
    print("\nSupprimés :")
    for r in removed:
        print("  - " + line(r))
    print("\nModifiés :")
    for before, after in modified:
        if before["libelle"] != after["libelle"]:
            print(f"  ~ {after['code']} : « {before['libelle']} » -> « {after['libelle']} »")
        if before["systeme"] != after["systeme"]:
            print(f"  ~ {after['code']} : système {before['systeme']} -> {after['systeme']}")
    return 0


# --------------------------------------------------------------------------
# Lecture des balances et des FEC
# --------------------------------------------------------------------------

def parse_number(text: str) -> float:
    value = (text or "").strip().replace(" ", "").replace(" ", "")
    if not value or value in {"-", "—"}:
        return 0.0
    negative = value.startswith("(") and value.endswith(")")
    value = value.strip("()")
    if "," in value and "." in value:
        decimal = "," if value.rfind(",") > value.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        value = value.replace(thousands, "").replace(decimal, ".")
    elif "," in value:
        head, _, tail = value.rpartition(",")
        value = (head + "." + tail) if len(tail) in (1, 2) and "," not in head else value.replace(",", "")
    number = float(value)
    return -number if negative else number


def find_column(headers: list[str], *needles: str, avoid: tuple = ()):
    """Colonne dont l'en-tête est exactement un des termes, sinon qui en contient un."""
    for index, header in enumerate(headers):
        if header in needles:
            return index
    for index, header in enumerate(headers):
        if any(n in header for n in needles) and not any(a in header for a in avoid):
            return index
    return None


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def detect_delimiter(header_line: str) -> str:
    return max(["\t", "|", ";", ","], key=header_line.count)


def read_balance(path: Path):
    text = read_text(path)
    first = text.splitlines()[0] if text else ""
    rows = list(csv.reader(io.StringIO(text), delimiter=detect_delimiter(first)))
    if len(rows) < 2:
        sys.exit("Balance vide ou sans en-tête.")
    headers = [norm(h).strip() for h in rows[0]]
    skip = ("lib", "intitule", "libelle")
    i_code = find_column(headers, "compte", "comptenum", "code", "numero", "account", avoid=skip)
    i_debit = find_column(headers, "debit")
    i_credit = find_column(headers, "credit")
    i_solde = find_column(headers, "solde")
    if i_code is None or (i_debit is None and i_credit is None and i_solde is None):
        sys.exit("Colonnes attendues : compte (ou code), debit, credit (ou solde).")
    entries, ignored = {}, []
    for raw in rows[1:]:
        if not any(cell.strip() for cell in raw):
            continue
        cell = raw[i_code].strip() if i_code < len(raw) else ""
        code = cell.replace(" ", "")
        if not re.fullmatch(r"\d+", code):
            ignored.append(cell or "?")
            continue

        def get(i):
            return parse_number(raw[i]) if i is not None and i < len(raw) else 0.0

        debit, credit = get(i_debit), get(i_credit)
        if i_debit is None and i_credit is None:
            solde = get(i_solde)
            debit, credit = (solde, 0.0) if solde >= 0 else (0.0, -solde)
        slot = entries.setdefault(code, [0.0, 0.0])
        slot[0] += debit
        slot[1] += credit
    return entries, ignored


def read_fec(path: Path):
    """Agrège un FEC par compte et contrôle l'équilibre de chaque écriture."""
    text = read_text(path)
    first = text.splitlines()[0] if text else ""
    rows = list(csv.reader(io.StringIO(text), delimiter=detect_delimiter(first)))
    if len(rows) < 2:
        sys.exit("FEC vide ou sans en-tête.")
    headers = [norm(h).strip() for h in rows[0]]
    idx = {name: headers.index(name) if name in headers else None
           for name in ("comptenum", "debit", "credit", "ecriturenum", "journalcode")}
    missing = [n for n in ("comptenum", "debit", "credit") if idx[n] is None]
    if missing:
        sys.exit("Colonnes FEC manquantes : " + ", ".join(missing)
                 + ". Le FEC doit contenir CompteNum, Debit et Credit.")
    entries, ignored, ecritures = {}, [], {}
    lines = 0
    for raw in rows[1:]:
        if not any(cell.strip() for cell in raw):
            continue
        lines += 1
        cell = raw[idx["comptenum"]].strip() if idx["comptenum"] < len(raw) else ""
        code = cell.replace(" ", "")
        debit = parse_number(raw[idx["debit"]]) if idx["debit"] < len(raw) else 0.0
        credit = parse_number(raw[idx["credit"]]) if idx["credit"] < len(raw) else 0.0
        if not re.fullmatch(r"\d+", code):
            ignored.append(cell or "?")
            continue
        slot = entries.setdefault(code, [0.0, 0.0])
        slot[0] += debit
        slot[1] += credit
        if idx["ecriturenum"] is not None:
            journal = raw[idx["journalcode"]].strip() if idx["journalcode"] is not None and idx["journalcode"] < len(raw) else ""
            key = (journal, raw[idx["ecriturenum"]].strip() if idx["ecriturenum"] < len(raw) else "")
            pair = ecritures.setdefault(key, [0.0, 0.0])
            pair[0] += debit
            pair[1] += credit
    desequilibrees = [
        {"journal": j, "ecriture": n, "ecart": round(d - c, 2)}
        for (j, n), (d, c) in ecritures.items() if abs(d - c) > TOL
    ]
    return entries, ignored, {"lignes": lines, "ecritures": len(ecritures), "ecritures_desequilibrees": desequilibrees}


# --------------------------------------------------------------------------
# Analyse commune balance et FEC
# --------------------------------------------------------------------------

def money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def analyse(entries, ignored, plan):
    total_d = sum(d for d, _ in entries.values())
    total_c = sum(c for _, c in entries.values())
    gap = round(total_d - total_c, 2)
    unknown, auxiliaires, contre_sens, attente = [], [], [], []
    charges = produits = 0.0
    for code, (debit, credit) in sorted(entries.items()):
        net = debit - credit
        account, exact = resolve(code, plan)
        if account is None:
            unknown.append(code)
        elif not exact and len(code) > MAX_PLAN_DIGITS:
            auxiliaires.append((code, account["code"]))
        elif not exact:
            unknown.append(code)
        if account and abs(net) > TOL:
            sens = account["sens_usuel"]
            if (sens == "debit" and net < 0) or (sens == "credit" and net > 0):
                contre_sens.append((code, account["libelle"], net))
        if code.startswith(("47", "58")) and abs(net) > TOL:
            attente.append((code, net))
        if code[0] == "6":
            charges += net
        elif code[0] == "7":
            produits -= net
    gestion = any(c[0] in "67" for c in entries)
    resultat = produits - charges
    return {
        "total_debit": round(total_d, 2),
        "total_credit": round(total_c, 2),
        "ecart": gap,
        "equilibree": abs(gap) <= TOL,
        "comptes": len(entries),
        "lignes_ignorees": ignored,
        "codes_inconnus": unknown,
        "auxiliaires_rattaches": auxiliaires,
        "contre_sens": [{"compte": c, "libelle": l, "solde": round(n, 2)} for c, l, n in contre_sens],
        "comptes_attente_non_soldes": [{"compte": c, "solde": round(n, 2)} for c, n in attente],
        "charges_classe6": round(charges, 2) if gestion else None,
        "produits_classe7": round(produits, 2) if gestion else None,
        "resultat": round(resultat, 2) if gestion else None,
    }


def print_report(report, plan, extra=None):
    print(f"Comptes lus : {report['comptes']}")
    print(f"Total débit  : {money(report['total_debit'])}")
    print(f"Total crédit : {money(report['total_credit'])}")
    if report["equilibree"]:
        print("Équilibre : OK")
    else:
        print(f"Équilibre : ÉCART de {money(report['ecart'])} (débit moins crédit). S'arrêter et corriger avant la clôture.")
    if extra:
        print(f"Lignes de FEC : {extra['lignes']}, écritures : {extra['ecritures']}")
        bad = extra["ecritures_desequilibrees"]
        if bad:
            print(f"Écritures déséquilibrées ({len(bad)}) :")
            for item in bad[:20]:
                print(f"  journal {item['journal'] or '?'} écriture {item['ecriture']} : écart {money(item['ecart'])}")
            if len(bad) > 20:
                print(f"  ... {len(bad) - 20} autres")
        else:
            print("Écritures : toutes équilibrées")
    if report["lignes_ignorees"]:
        shown = ", ".join(report["lignes_ignorees"][:10])
        print(f"Lignes ignorées (compte non numérique, par exemple totaux) : {shown}")
    if report["codes_inconnus"]:
        print("Codes absents du plan :")
        for code in report["codes_inconnus"]:
            near = ", ".join(r["code"] for r in suggestions(code, plan, 4)) or "aucun"
            print(f"  {code}  (voisins : {near})")
    if report["auxiliaires_rattaches"]:
        first = report["auxiliaires_rattaches"][0]
        print(f"Comptes de l'entité rattachés au plan : {len(report['auxiliaires_rattaches'])} (ex. {first[0]} -> {first[1]})")
    if report["contre_sens"]:
        print("Soldes à contre-sens (à examiner) :")
        for item in report["contre_sens"]:
            side = "débiteur" if item["solde"] > 0 else "créditeur"
            print(f"  {item['compte']} {item['libelle']} : solde {side} de {money(abs(item['solde']))}")
    if report["comptes_attente_non_soldes"]:
        print("Comptes d'attente (47) ou virements internes (58) non soldés :")
        for item in report["comptes_attente_non_soldes"]:
            print(f"  {item['compte']} : {money(item['solde'])}")
    if report["resultat"] is not None:
        label = "bénéfice" if report["resultat"] >= 0 else "perte"
        print("Résultat provisoire (classes 6 et 7) :")
        print(f"  Charges (classe 6)   : {money(report['charges_classe6'])}")
        print(f"  Produits (classe 7)  : {money(report['produits_classe7'])}")
        print(f"  Résultat             : {money(report['resultat'])} ({label})")
    else:
        print("Aucun compte de gestion (6, 7) : résultat non calculable ou exercice déjà soldé (120 ou 129).")


def cmd_balance(args, plan):
    entries, ignored = read_balance(Path(args.fichier))
    report = analyse(entries, ignored, plan)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report, plan)
    return 0 if report["equilibree"] else 1


def cmd_fec(args, plan):
    entries, ignored, extra = read_fec(Path(args.fichier))
    report = analyse(entries, ignored, plan)
    report["fec"] = extra
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report, plan, extra)
    ok = report["equilibree"] and not extra["ecritures_desequilibrees"]
    return 0 if ok else 1


# --------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan comptable général (PCG) français")
    parser.add_argument("--annee", type=int, default=DEFAULT_YEAR, help="Version du plan (2025 ou 2026)")
    parser.add_argument("--plan", help="Chemin d'un fichier plan-comptable-AAAA.csv")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("find", help="Fiche d'un compte")
    p.add_argument("code")
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("search", help="Recherche sur le code ou le libellé")
    p.add_argument("terme")
    p.add_argument("--classe", type=int)
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("validate", help="Valider des codes (ou - pour lire stdin)")
    p.add_argument("codes", nargs="+")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("tree", help="Descendants d'un compte")
    p.add_argument("code")
    p.add_argument("--depth", type=int)
    p.set_defaults(func=cmd_tree)

    p = sub.add_parser("classe", help="Comptes d'une classe")
    p.add_argument("numero", type=int)
    p.add_argument("--niveau", type=int)
    p.set_defaults(func=cmd_classe)

    p = sub.add_parser("export", help="Exporter le plan (csv, json, md)")
    p.add_argument("--format", choices=["csv", "json", "md"], default="csv")
    p.add_argument("--classe", type=int)
    p.add_argument("--niveau", type=int)
    p.add_argument("--nature", choices=["bilan", "gestion", "special"])
    p.add_argument("--sens", choices=["debit", "credit", "mixte"])
    p.add_argument("--systeme", choices=["minimal", "facultatif", "condensed", "base", "developed"])
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("stats", help="Statistiques du plan")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("diff", help="Différences entre deux années du plan")
    p.add_argument("--de", type=int, default=2025)
    p.add_argument("--vers", type=int, default=2026)
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("balance", help="Contrôler une balance (CSV) et calculer le résultat")
    p.add_argument("fichier")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_balance)

    p = sub.add_parser("fec", help="Lire un FEC : balance reconstituée, contrôle des écritures, résultat")
    p.add_argument("fichier")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_fec)
    return parser


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    plan = load_plan(plan_path(args.annee, args.plan))
    try:
        return args.func(args, plan)
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
