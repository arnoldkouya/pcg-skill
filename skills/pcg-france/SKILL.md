---
name: pcg-france
description: Comptabilité française selon le Plan comptable général (PCG). Retrouver, valider et expliquer un compte (versions 2023 à 2026 du plan), proposer une imputation, contrôler une balance ou un FEC, calculer le résultat et les soldes intermédiaires de gestion, préparer les écritures d'inventaire, le bilan et le compte de résultat. À utiliser dès qu'un numéro de compte PCG (411, 44571, 6811…), un FEC, une balance, une clôture d'exercice ou la réforme du PCG 2025 est mentionné. Pas pour le SYSCOHADA/OHADA ni l'IFRS.
---

# PCG français : plan comptable, imputation et clôture

Ce skill couvre le Plan comptable général français (règlement ANC n° 2014-03 modifié, dont la réforme ANC 2022-06 applicable aux exercices ouverts depuis le 1er janvier 2025) : trouver un compte, imputer une opération, contrôler une balance ou un FEC, calculer le résultat, préparer la clôture.

## Ressources du skill

Les chemins sont relatifs au dossier de ce skill.

| Fichier | Usage |
|---|---|
| `references/plan-comptable-2026.csv` | Plan en vigueur : 861 comptes, colonnes `code, libelle, classe, niveau, parent, systeme, nature, sens_usuel` |
| `references/plan-comptable-2025.csv` | Plan 2025, première version issue de la réforme ANC 2022-06 (861 comptes) |
| `references/plan-comptable-2024.csv`, `plan-comptable-2023.csv` | Plans d'avant la réforme (1025 comptes), pour les exercices ouverts avant le 1er janvier 2025 |
| `references/cloture.md` | Clôture : réforme 2025, SIG, écritures d'inventaire, TVA, impôt, affectation, états financiers. À lire avant toute tâche de clôture. |
| `scripts/pcg.py` | Outil en ligne de commande (Python 3, bibliothèque standard) : recherche, validation, arbre, export, différences entre années, contrôle de balance, lecture d'un FEC |

Choisir la version du plan selon la date d'ouverture de l'exercice : 2026 par défaut ; `--annee 2025` pour un exercice ouvert en 2025 ; `--annee 2024` ou `--annee 2023` pour un exercice ouvert avant le 1er janvier 2025. Demander la date d'ouverture de l'exercice si elle n'est pas connue. Ne jamais citer un compte ou un libellé de mémoire : le chercher dans le CSV ou avec le script. Le plan a été profondément remanié en 2025 (plus de 200 comptes supprimés, dont les transferts de charges 79 et les comptes de cessions 675 et 775) : une imputation connue d'avant 2025 doit être revérifiée.

## Utiliser le script

```bash
python3 scripts/pcg.py find 6811                  # fiche, chemin hiérarchique, enfants
python3 scripts/pcg.py search "clients douteux"    # insensible à la casse et aux accents
python3 scripts/pcg.py validate 411 44571 9999 ABC
python3 scripts/pcg.py tree 44 --depth 2
python3 scripts/pcg.py classe 5 --niveau 3
python3 scripts/pcg.py export --format csv --classe 6 > classe6.csv
python3 scripts/pcg.py diff                        # changements 2025 -> 2026
python3 scripts/pcg.py diff --de 2024 --vers 2025  # effet de la réforme
python3 scripts/pcg.py balance balance.csv         # contrôle + résultat
python3 scripts/pcg.py fec FEC.txt                 # balance reconstituée + contrôle des écritures
```

Ajouter `--annee AAAA` avant la commande pour une autre version du plan et `--json` à `validate`, `balance` et `fec` pour une sortie exploitable. Si Python n'est pas disponible, lire directement les CSV.

## Structure du plan

Un code a 1 à 5 chiffres dans le plan (les comptes plus fins sont propres à l'entité). Le premier chiffre est la classe, la longueur est le niveau, le parent s'obtient en retirant le dernier chiffre. La colonne `systeme` vaut `minimal` ou `facultatif` dans les plans 2025 et 2026, et `condensed` (système abrégé), `base` (système de base) ou `developed` (système développé, qui contient tous les comptes du système de base, lui-même contenant ceux du système abrégé) dans les plans 2023 et 2024.

| Classe | Contenu | Nature |
|---|---|---|
| 1 | Capitaux (10 capital et réserves, 11 report à nouveau, 12 résultat, 13 subventions, 14 provisions réglementées, 15 provisions, 16 emprunts) | bilan |
| 2 | Immobilisations (20 incorporelles, 21 corporelles, 26-27 financières, 28 amortissements, 29 dépréciations) | bilan |
| 3 | Stocks et en-cours (39 dépréciations) | bilan |
| 4 | Tiers (40 fournisseurs, 41 clients, 42 personnel, 43 organismes sociaux, 44 État, 45 groupe et associés, 46 divers, 47 attente, 48 régularisation, 49 dépréciations) | bilan |
| 5 | Comptes financiers (50 VMP, 51 banques, 53 caisse, 58 virements internes, 59 dépréciations) | bilan |
| 6 | Charges (60 achats, 61-62 services extérieurs, 63 impôts et taxes, 64 personnel, 65 gestion courante, 66 financières, 67 exceptionnelles, 68 dotations, 69 participation et impôt sur les bénéfices) | gestion |
| 7 | Produits (70 ventes et prestations, 71 production stockée, 72 production immobilisée, 74 subventions, 75 gestion courante, 76 financiers, 77 exceptionnels, 78 reprises) | gestion |
| 8 | Comptes spéciaux (engagements, résultat en instance d'affectation) | special |

La colonne `sens_usuel` (debit, credit, mixte) est un repère indicatif calculé par préfixe, pas le texte du PCG. Les comptes mixtes (la plupart des comptes de tiers, 51 banques, 603 et 71 variations de stocks) peuvent être débiteurs ou créditeurs. En cas de doute sur le fonctionnement d'un compte, s'appuyer sur le PCG et le dire.

## Méthodes

### Retrouver ou valider un compte
1. Vérifier le format (chiffres uniquement).
2. Chercher le compte dans le plan de la bonne année. S'il n'existe pas, le dire et proposer les comptes voisins.
3. Restituer code, libellé, classe, niveau, parent, système, sens usuel et chemin hiérarchique.
4. Un code de plus de 5 chiffres, ou un compte auxiliaire de l'entité, se rattache à son préfixe existant dans le plan.

### Proposer une imputation
1. Qualifier l'opération (achat, vente, paie, immobilisation, TVA, financement, impôt, etc.) et l'exercice concerné.
2. Partir de la classe, descendre au niveau le plus fin utile, vérifier chaque code dans le plan de l'année.
3. Donner l'écriture équilibrée en tableau (Compte, Libellé, Débit, Crédit) avec une justification d'une ligne par compte.
4. Poser une question quand c'est ambigu (TVA déductible ou non, charge ou immobilisation, nature de l'opération) plutôt que de deviner. Préciser que l'imputation finale relève de l'expert-comptable de l'entité et de son plan de comptes.

### Valider un lot de codes
Rendre trois listes : valides, invalides, format incorrect, avec les comptes voisins pour chaque invalide.

### Contrôler une balance ou un FEC, puis clore
1. Lancer `balance` (fichier CSV) ou `fec` (fichier des écritures comptables) : équilibre débit/crédit, codes inconnus, soldes à contre-sens, comptes d'attente non soldés, résultat provisoire. Pour un FEC, le script vérifie aussi l'équilibre de chaque écriture.
2. Si l'équilibre est rompu, s'arrêter et présenter l'écart avant tout autre calcul.
3. Lire `references/cloture.md`, puis dérouler : écritures d'inventaire, TVA, impôt, soldes intermédiaires, états financiers, affectation.
4. Demander les données manquantes (dates de mise en service, taux, durées, régime fiscal) au lieu de les inventer.
5. Vérifier par calcul : total débit égal total crédit dans chaque écriture, résultat des SIG égal produits moins charges, total actif égal total passif.

## Livrables

- Question ponctuelle sur un compte : réponse courte en prose (code, libellé, remarque utile).
- Imputation : tableau d'écriture, puis une ligne de justification.
- Lot de codes ou export du plan : fichier CSV, JSON ou XLSX selon la demande, avec un résumé de deux phrases.
- Clôture à partir d'un fichier : un classeur avec les onglets Balance contrôlée, SIG, Écritures d'inventaire, Bilan, Compte de résultat, et des formules plutôt que des valeurs en dur. Terminer par les hypothèses prises et les informations manquantes.

## Limites à annoncer

- Les données du plan viennent du dépôt ouvert arrhes/PCG, établi à partir des textes de l'ANC. Pour un usage officiel (liasse fiscale, dépôt des comptes, commissariat aux comptes), recouper avec le règlement ANC en vigueur et les sources de l'ANC.
- Les formules de SIG et les modèles d'états financiers sont une trame de travail ; le modèle réglementaire dépend de la taille de l'entité et du régime (système de base, abrégé, développé).
- Pas de conseil fiscal : taux d'impôt sur les sociétés, régimes de TVA, déductibilité et formulaires de liasse changent chaque année. Renvoyer vers impots.gouv.fr ou un professionnel et ne pas figer de taux.
- Le skill ne couvre ni le plan comptable des associations, des assurances ou des secteurs spécifiques, ni les normes IFRS.
- Le résultat est un travail préparatoire qui doit être validé par un expert-comptable.
