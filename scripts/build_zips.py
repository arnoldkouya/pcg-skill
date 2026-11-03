#!/usr/bin/env python3
"""Construit les archives de distribution dans dist/.

- dist/pcg-france-skill.zip : dossier pcg-france/ à la racine de l'archive, prêt
  pour l'import d'un skill dans Claude (claude.ai, Desktop) ou ChatGPT.
- dist/pcg-france-gpt-pack.zip : instructions et fichiers de connaissance pour un
  GPT personnalisé (voir chatgpt/README.md).
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "pcg-france"
DIST = ROOT / "dist"


def add_tree(archive: zipfile.ZipFile, source: Path, arcroot: str) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_dir() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        archive.write(path, f"{arcroot}/{path.relative_to(source).as_posix()}")


def main() -> None:
    DIST.mkdir(exist_ok=True)

    skill_zip = DIST / "pcg-france-skill.zip"
    with zipfile.ZipFile(skill_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        add_tree(archive, SKILL, "pcg-france")

    pack_zip = DIST / "pcg-france-gpt-pack.zip"
    with zipfile.ZipFile(pack_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / "chatgpt" / "instructions.md", "instructions.md")
        for year in (2026, 2025, 2024, 2023):
            name = f"plan-comptable-{year}.csv"
            archive.write(SKILL / "references" / name, name)
        archive.write(SKILL / "references" / "cloture.md", "cloture.md")
        archive.write(SKILL / "scripts" / "pcg.py", "pcg.py")
        archive.write(ROOT / "chatgpt" / "README.md", "LISEZMOI.md")

    for path in (skill_zip, pack_zip):
        print(f"{path.relative_to(ROOT)}  ({path.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
