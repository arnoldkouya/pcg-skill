# pcg-skill

[English](README.md) | **Français**

Skill pour agents IA dédié à la comptabilité française selon le **Plan comptable général (PCG)** : plans 2023 à 2026 (861 comptes depuis la réforme de 2025), imputation, contrôle de balance et de FEC, résultat, soldes intermédiaires de gestion et écritures de clôture.

Un seul skill, installable sur **Claude** (Claude Code, claude.ai, Desktop), **Codex** et **ChatGPT**, car il suit le format ouvert Agent Skills (un dossier avec un fichier `SKILL.md`). Son équivalent pour l'espace OHADA est [syscohada-skill](https://github.com/arnoldkouya/syscohada-skill).

## Ce que fait le skill

- **Plan comptable** : retrouver, expliquer et valider un compte (versions 2023 à 2026, selon la date d'ouverture de l'exercice), avec libellé, niveau, parent, système (minimal ou facultatif depuis 2025 ; abrégé, de base ou développé avant), sens usuel et chemin hiérarchique.
- **Réforme 2025** (règlement ANC 2022-06) : le skill connaît les comptes supprimés (79, 675, 775, 777) et leurs remplaçants (649, 7587, 657, 757, 747), et la commande `diff` compare les années.
- **Imputation** : proposer l'écriture d'une opération avec débit et crédit équilibrés et une justification par compte.
- **Contrôle de balance et de FEC** : équilibre, codes inconnus, soldes à contre-sens, comptes d'attente non soldés, équilibre de chaque écriture du FEC, résultat provisoire.
- **Clôture** : écritures d'inventaire (amortissements, dépréciations, provisions, stocks, charges à payer, produits à recevoir, régularisations, créances douteuses, cessions, impôt), TVA, soldes intermédiaires de gestion, bilan, compte de résultat, affectation du résultat.
- **Exports** du plan en CSV, JSON ou Markdown.

## Installation

| Plateforme | Méthode |
|---|---|
| Claude Code | Plugin ou script (voir ci-dessous) |
| Claude (claude.ai, Desktop) | Importer `dist/pcg-france-skill.zip` dans les réglages des skills |
| Codex | Script d'installation ou copie dans `~/.agents/skills/pcg-france` |
| ChatGPT | Skill (bêta) ou GPT personnalisé : voir [chatgpt/README.md](chatgpt/README.md) |
| Autre agent compatible Agent Skills | Copier `skills/pcg-france/` dans le dossier de skills de l'agent |

### Cloner le dépôt

```bash
git clone https://github.com/arnoldkouya/pcg-skill.git
cd pcg-skill
```

### Claude Code

Par le plugin :

```text
/plugin marketplace add arnoldkouya/pcg-skill
/plugin install pcg-france@pcg-skill
```

Ou par le script, qui copie le skill dans `~/.claude/skills/pcg-france` :

```bash
scripts/install.sh claude            # pour tous vos projets
scripts/install.sh claude --project  # pour le projet courant (.claude/skills)
```

### Claude (claude.ai, Desktop)

```bash
python3 scripts/build_zips.py
```

Puis, dans les réglages de Claude, section des capacités ou des skills, importer `dist/pcg-france-skill.zip` (le dossier `pcg-france/` est à la racine de l'archive). L'intitulé exact du menu varie selon la version de l'application.

### Codex

```bash
scripts/install.sh codex            # ~/.agents/skills/pcg-france
scripts/install.sh codex --project  # .agents/skills du projet courant
```

Sous Windows, utiliser `scripts\install.ps1 -Target codex` (ou `claude`, `all`, avec `-Project` pour le projet courant). Dans Codex, le skill s'active seul selon la description, ou en le nommant : `$pcg-france`.

### ChatGPT

Voir [chatgpt/README.md](chatgpt/README.md) : import comme skill (bêta, à activer dans l'espace de travail) ou GPT personnalisé avec `dist/pcg-france-gpt-pack.zip`.

## Exemples de demandes

- « Quel compte utiliser pour une prime d'assurance ? »
- « Valide ces codes : 411 44571 9999 ABC »
- « Qu'est-ce qui a changé dans le PCG en 2025 pour les cessions d'immobilisations ? »
- « Voici ma balance, contrôle-la et donne le résultat. »
- « Contrôle ce FEC avant l'envoi à mon expert-comptable. »
- « Prépare les écritures de clôture : amortissements, charges à payer, impôt. »

## Utiliser le script seul

`skills/pcg-france/scripts/pcg.py` fonctionne sans l'agent (Python 3.8 ou plus, aucune dépendance) :

```bash
python3 skills/pcg-france/scripts/pcg.py find 6811
python3 skills/pcg-france/scripts/pcg.py search "clients douteux"
python3 skills/pcg-france/scripts/pcg.py validate 411 44571 9999
python3 skills/pcg-france/scripts/pcg.py tree 44 --depth 2
python3 skills/pcg-france/scripts/pcg.py export --format csv --classe 6
python3 skills/pcg-france/scripts/pcg.py diff                       # 2025 -> 2026
python3 skills/pcg-france/scripts/pcg.py --annee 2024 find 675      # plan d'avant la réforme
python3 skills/pcg-france/scripts/pcg.py diff --de 2024 --vers 2025 # effet de la réforme
python3 skills/pcg-france/scripts/pcg.py balance examples/balance-exemple.csv
python3 skills/pcg-france/scripts/pcg.py fec examples/fec-exemple.txt
```

- **Balance** : un CSV avec les colonnes `compte`, `debit`, `credit` (ou `solde`, positif au débit). Séparateurs `,`, `;` et tabulation, nombres au format `1 234,56` ou `1,234.56`, lignes de total ignorées. Les comptes de plus de 5 chiffres (comptes de l'entité) sont rattachés à leur préfixe du plan.
- **FEC** : séparateur tabulation, barre verticale ou point-virgule, encodage UTF-8 ou Windows-1252 détectés. Colonnes requises : `CompteNum`, `Debit`, `Credit` ; `JournalCode` et `EcritureNum` pour le contrôle de chaque écriture.
- Le code de sortie est 1 si la balance ou une écriture est déséquilibrée.

## Structure du dépôt

```text
skills/pcg-france/
├── SKILL.md                         # le skill
├── references/
│   ├── plan-comptable-2026.csv      # 861 comptes
│   ├── plan-comptable-2025.csv      # 861 comptes
│   ├── plan-comptable-2024.csv      # 1025 comptes (avant la réforme)
│   ├── plan-comptable-2023.csv
│   └── cloture.md                   # réforme 2025, SIG, écritures d'inventaire, TVA, FEC
└── scripts/pcg.py                   # recherche, validation, diff, balance, FEC
.claude-plugin/                      # manifestes du plugin Claude Code
chatgpt/                             # instructions et guide pour ChatGPT
scripts/                             # install.sh, install.ps1, build_zips.py, build_plan.py
examples/                            # balance-exemple.csv, fec-exemple.txt
tests/test_pcg.py
NOTICE.md                            # sources et licences des données
AGENTS.md                            # consignes pour les agents qui modifient ce dépôt
```

## Développement

```bash
python3 -m unittest discover -s tests -v   # tests
python3 scripts/build_zips.py              # archives dans dist/
python3 scripts/build_plan.py CHEMIN_ARRHES_PCG              # régénérer les plans 2023 à 2026 (voir AGENTS.md)
```

## Projets proches

- [arrhes/PCG](https://github.com/arrhes/PCG) : la source des données du plan, au format JSON (CC0).
- [romainsimon/paperasse](https://github.com/romainsimon/paperasse) : un skill plus large sur la comptabilité, la fiscalité et la facturation françaises (TVA, liasse, facturation électronique). Ce dépôt-ci est plus étroit : plan comptable embarqué, contrôle de balance et de FEC, clôture.

## Limites

- Les données viennent d'arrhes/PCG, établies à partir des textes de l'ANC (voir [NOTICE.md](NOTICE.md)). Pour une liasse destinée à l'administration, un dépôt de comptes ou un commissaire aux comptes, recouper avec le règlement ANC en vigueur.
- Le sens usuel des comptes est un repère indicatif calculé par préfixe, pas le texte du PCG.
- Les formules de SIG et les modèles d'états financiers sont une trame de travail, à aligner sur le système comptable de l'entité (base, abrégé, développé).
- Aucun conseil fiscal : taux d'impôt sur les sociétés, régimes de TVA et formulaires de liasse changent chaque année et ne sont pas figés dans le skill.
- Le skill ne couvre ni les plans sectoriels (associations, assurances), ni les normes IFRS.
- Le résultat est un travail préparatoire qui doit être validé par un expert-comptable.

## Sources de la réforme 2025

Résumé établi à partir de la page [Cegid sur le nouveau plan comptable 2025](https://www.cegid.com/fr/blog/nouveau-plan-comptable-2025-nouveautes-application-tpe/) et du projet de règlement présenté par [Legifiscal](https://www.legifiscal.fr/actualites-fiscales/3087-comptabilite-reforme-resultat-exceptionnel-suppression-transferts-charges.html), puis recoupé avec le plan lui-même (comptes présents ou absents).

## Licence

MIT pour le code et les textes de ce dépôt, voir [LICENSE](LICENSE). Les données du plan ont leur propre régime, voir [NOTICE.md](NOTICE.md).
