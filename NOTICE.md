# Sources et attributions

## Données du plan comptable

Les fichiers `skills/pcg-france/references/plan-comptable-AAAA.csv` (2023 à 2026) sont générés à partir des données ouvertes du dépôt [arrhes/PCG](https://github.com/arrhes/PCG) (fichiers `PCG/versions/AAAA/pcg_AAAA.json`).

- Le dépôt arrhes/PCG est publié sous licence CC0 1.0. Le jeu de données « Plan Comptable Général » publié par Arrhes sur data.gouv.fr est sous Licence Ouverte 2.0 (Etalab) : paternité à mentionner, ce que fait ce fichier.
- Le contenu du plan reprend le Plan comptable général de l'Autorité des normes comptables (ANC), règlement n° 2014-03 modifié, dont le règlement n° 2022-06 applicable aux exercices ouverts à compter du 1er janvier 2025.
- Les colonnes `nature` et `sens_usuel` ne figurent pas dans la source : elles sont calculées par `scripts/build_plan.py` (nature selon la classe, sens usuel par préfixe). Le sens usuel est un repère indicatif.
- Les textes officiels d'origine (PDF de l'ANC) sont dans le dépôt arrhes/PCG, dossier `PCG/sources`.

## Limites

Ce dépôt n'est ni un texte officiel ni un produit de l'ANC. Pour un usage réglementaire, se référer au règlement de l'ANC en vigueur.
