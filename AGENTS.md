# Instructions pour les agents qui modifient ce dépôt

Ce dépôt contient un seul skill, `skills/pcg-france/`, au format Agent Skills (dossier avec `SKILL.md`, `references/`, `scripts/`).

## Règles

- Source de vérité du skill : `skills/pcg-france/`. Ne pas dupliquer son contenu ailleurs ; les scripts d'installation et de packaging le copient.
- `SKILL.md` doit garder un frontmatter avec `name: pcg-france` et une `description` de moins de 1024 caractères.
- Les fichiers `references/plan-comptable-AAAA.csv` sont générés par `scripts/build_plan.py` à partir du dépôt arrhes/PCG. Ne pas les éditer à la main : modifier le script (par exemple la table `OVERRIDES` du sens usuel) et régénérer.
- Tout code cité dans `references/cloture.md` ou `SKILL.md` doit exister dans le plan de l'année, sauf quand le texte dit explicitement qu'il a été supprimé. Vérifier avec `python3 skills/pcg-france/scripts/pcg.py find CODE`.
- `scripts/pcg.py` n'utilise que la bibliothèque standard Python (3.8+). Ne pas ajouter de dépendance.
- `chatgpt/instructions.md` doit rester sous 8 000 caractères (limite des GPT personnalisés).
- Ne jamais figer de taux d'impôt, de régime de TVA ou de numéro de formulaire dans le skill : ces éléments changent chaque année.

## Mise à jour annuelle du plan

1. Récupérer la nouvelle version dans arrhes/PCG (`PCG/versions/AAAA/pcg_AAAA.json`).
2. `python3 scripts/build_plan.py CHEMIN_DEPOT_ARRHES` (toutes les années) ou en précisant les années à générer.
3. Passer `DEFAULT_YEAR` de `scripts/pcg.py` à la nouvelle année et mettre à jour les tests (effectifs, `diff`) et les mentions de millésime dans `SKILL.md` et le README.
4. Relire `references/cloture.md` : chaque code cité doit exister dans le nouveau plan.

## Vérifications avant de livrer

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_zips.py
```
