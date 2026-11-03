#!/usr/bin/env python3
"""Génère les CSV du plan comptable général (PCG) depuis les données ouvertes.

Source : https://github.com/arrhes/PCG (dossier PCG/versions/AAAA/pcg_AAAA.json),
données issues du règlement ANC n° 2014-03 (Licence Ouverte 2.0, dépôt en CC0).

Usage : python3 scripts/build_plan.py CHEMIN_DEPOT_ARRHES [ANNEE ...]
Écrit skills/pcg-france/references/plan-comptable-AAAA.csv.

La colonne sens_usuel est calculée ici (le JSON source ne la contient pas) par
préfixe le plus long : c'est un repère indicatif, pas le texte du PCG.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "skills" / "pcg-france" / "references"

CLASS_SENS = {"1": "credit", "2": "debit", "3": "debit", "4": "mixte",
              "5": "debit", "6": "debit", "7": "credit", "8": "mixte"}
NATURE = {"1": "bilan", "2": "bilan", "3": "bilan", "4": "bilan", "5": "bilan",
          "6": "gestion", "7": "gestion", "8": "special"}

# Exceptions au sens de la classe, appliquées par préfixe le plus long.
OVERRIDES = {
    "108": "mixte", "109": "debit",
    "11": "mixte", "110": "credit", "119": "debit",
    "12": "mixte", "120": "credit", "129": "debit",
    "139": "debit", "169": "debit", "18": "mixte",
    "28": "credit", "29": "credit", "39": "credit",
    "40": "credit", "408": "credit", "409": "debit",
    "41": "debit", "418": "debit", "419": "credit",
    "486": "debit", "487": "credit", "49": "credit",
    "4455": "credit", "4456": "debit", "4457": "credit",
    "511": "debit", "51": "mixte", "519": "credit", "52": "mixte", "59": "credit",
    "603": "mixte", "609": "credit", "619": "credit", "629": "credit",
    "709": "debit", "71": "mixte",
}


def sens_usuel(code: str) -> str:
    for size in range(len(code), 0, -1):
        if code[:size] in OVERRIDES:
            return OVERRIDES[code[:size]]
    return CLASS_SENS[code[0]]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    repo = Path(sys.argv[1])
    years = [int(y) for y in sys.argv[2:]] or [2023, 2024, 2025, 2026]
    OUT.mkdir(parents=True, exist_ok=True)
    for year in years:
        data = json.loads((repo / "PCG" / "versions" / str(year) / f"pcg_{year}.json").read_text(encoding="utf-8"))
        rows = data["flat"]
        target = OUT / f"plan-comptable-{year}.csv"
        with open(target, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["code", "libelle", "classe", "niveau", "parent", "systeme", "nature", "sens_usuel"])
            for row in sorted(rows, key=lambda r: str(r["number"])):
                code = str(row["number"])
                writer.writerow([
                    code, " ".join(row["label"].split()), code[0], len(code),
                    "" if row["parent"] is None else row["parent"],
                    row["system"], NATURE[code[0]], sens_usuel(code),
                ])
        print(f"{target.relative_to(ROOT)} : {len(rows)} comptes")


if __name__ == "__main__":
    main()
