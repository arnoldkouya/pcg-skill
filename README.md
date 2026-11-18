# pcg-skill

**English** | [Français](README.fr.md)

AI agent skill for French accounting under the **Plan comptable général (PCG)**, the French national chart of accounts issued by the Autorité des normes comptables (ANC): charts from 2023 to 2026 (861 accounts since the 2025 reform), entry posting suggestions, trial balance and FEC checks, result calculation, intermediate management balances (SIG) and year-end closing entries. The FEC (Fichier des écritures comptables) is the standard French accounting entries export.

One skill, installable on **Claude** (Claude Code, claude.ai, Desktop), **Codex** and **ChatGPT**, because it follows the open Agent Skills format (a folder with a `SKILL.md` file). Its counterpart for the OHADA area is [syscohada-skill](https://github.com/arnoldkouya/syscohada-skill).

> **Language note:** the skill's instructions (`SKILL.md`), reference documents and the ChatGPT instructions are written in French, as is the accounting vocabulary of the chart of accounts. This README and the ChatGPT guide are available in English; translating the skill itself is a welcome contribution.

## What the skill does

- **Chart of accounts**: look up, explain and validate an account (versions 2023 to 2026, chosen by the date the financial year opened), with label, level, parent, system (minimal or optional since 2025; condensed, base or developed before), usual balance side and hierarchical path.
- **2025 reform** (ANC regulation 2022-06): the skill knows the removed accounts (79, 675, 775, 777) and their replacements (649, 7587, 657, 757, 747), and the `diff` command compares years.
- **Posting**: suggest the journal entry for a transaction, with balanced debit and credit and a one-line justification per account.
- **Trial balance and FEC checks**: debit/credit balance, unknown codes, balances on the unusual side, suspense accounts not cleared, balance of every FEC entry, provisional result.
- **Year-end closing**: adjusting entries (depreciation, impairment, provisions, inventory, accruals, deferrals, doubtful receivables, disposals, income tax), VAT, intermediate management balances, balance sheet, income statement, appropriation of the result.
- **Exports** of the chart as CSV, JSON or Markdown.

## Installation

| Platform | Method |
|---|---|
| Claude Code | Plugin or script (see below) |
| Claude (claude.ai, Desktop) | Import `dist/pcg-france-skill.zip` in the skills settings |
| Codex | Install script, or copy into `~/.agents/skills/pcg-france` |
| ChatGPT | Skill (beta) or custom GPT: see [chatgpt/README.en.md](chatgpt/README.en.md) |
| Any other Agent Skills compatible agent | Copy `skills/pcg-france/` into the agent's skills folder |

### Clone the repository

```bash
git clone https://github.com/arnoldkouya/pcg-skill.git
cd pcg-skill
```

### Claude Code

With the plugin:

```text
/plugin marketplace add arnoldkouya/pcg-skill
/plugin install pcg-france@pcg-skill
```

Or with the script, which copies the skill into `~/.claude/skills/pcg-france`:

```bash
scripts/install.sh claude            # for all your projects
scripts/install.sh claude --project  # for the current project (.claude/skills)
```

### Claude (claude.ai, Desktop)

```bash
python3 scripts/build_zips.py
```

Then, in Claude's settings (capabilities or skills section), import `dist/pcg-france-skill.zip` (the `pcg-france/` folder sits at the root of the archive). The exact menu name varies with the app version.

### Codex

```bash
scripts/install.sh codex            # ~/.agents/skills/pcg-france
scripts/install.sh codex --project  # .agents/skills of the current project
```

On Windows, use `scripts\install.ps1 -Target codex` (or `claude`, `all`, with `-Project` for the current project). In Codex the skill activates on its own based on its description, or by name: `$pcg-france`.

### ChatGPT

See [chatgpt/README.en.md](chatgpt/README.en.md): import as a skill (beta, to be enabled in the workspace) or a custom GPT with `dist/pcg-france-gpt-pack.zip`.

## Example requests

The skill is written in French; these are English renderings of the kind of request it handles.

- "Which account should I use for an insurance premium?"
- "Validate these codes: 411 44571 9999 ABC"
- "What changed in the PCG in 2025 for asset disposals?"
- "Here is my trial balance, check it and give me the result."
- "Check this FEC before I send it to my accountant."
- "Prepare the closing entries: depreciation, accruals, income tax."

## Using the script on its own

`skills/pcg-france/scripts/pcg.py` works without any agent (Python 3.8 or later, no dependencies):

```bash
python3 skills/pcg-france/scripts/pcg.py find 6811
python3 skills/pcg-france/scripts/pcg.py search "clients douteux"
python3 skills/pcg-france/scripts/pcg.py validate 411 44571 9999
python3 skills/pcg-france/scripts/pcg.py tree 44 --depth 2
python3 skills/pcg-france/scripts/pcg.py export --format csv --classe 6
python3 skills/pcg-france/scripts/pcg.py diff                       # 2025 -> 2026
python3 skills/pcg-france/scripts/pcg.py --annee 2024 find 675      # pre-reform chart
python3 skills/pcg-france/scripts/pcg.py diff --de 2024 --vers 2025 # effect of the reform
python3 skills/pcg-france/scripts/pcg.py balance examples/balance-exemple.csv
python3 skills/pcg-france/scripts/pcg.py fec examples/fec-exemple.txt
```

Account labels are in French, so searches use French terms. `--annee` selects the chart year and `--de`/`--vers` the two years to compare.

- **Trial balance**: a CSV with the columns `compte` (account), `debit`, `credit` (or `solde`, positive on the debit side). The separators `,`, `;` and tab, and numbers written `1 234,56` or `1,234.56`, are accepted; total rows are ignored. Accounts longer than 5 digits (the company's own sub-accounts) are attached to their prefix in the chart.
- **FEC**: tab, pipe or semicolon separator; UTF-8 or Windows-1252 encoding is detected. Required columns: `CompteNum`, `Debit`, `Credit`; `JournalCode` and `EcritureNum` for the per-entry balance check.
- The exit code is 1 when the trial balance or an entry does not balance.

## Repository layout

```text
skills/pcg-france/
├── SKILL.md                         # the skill
├── references/
│   ├── plan-comptable-2026.csv      # 861 accounts
│   ├── plan-comptable-2025.csv      # 861 accounts
│   ├── plan-comptable-2024.csv      # 1025 accounts (before the reform)
│   ├── plan-comptable-2023.csv
│   └── cloture.md                   # 2025 reform, SIG, adjusting entries, VAT, FEC
└── scripts/pcg.py                   # search, validation, diff, trial balance, FEC
.claude-plugin/                      # Claude Code plugin manifests
chatgpt/                             # instructions and guide for ChatGPT
scripts/                             # install.sh, install.ps1, build_zips.py, build_plan.py
examples/                            # balance-exemple.csv, fec-exemple.txt
tests/test_pcg.py
NOTICE.md                            # data sources and licenses
AGENTS.md                            # guidelines for agents that modify this repository
```

## Development

```bash
python3 -m unittest discover -s tests -v   # tests
python3 scripts/build_zips.py              # archives in dist/
python3 scripts/build_plan.py PATH_TO_ARRHES_PCG   # regenerate the 2023-2026 charts (see AGENTS.md)
```

## Related projects

- [arrhes/PCG](https://github.com/arrhes/PCG): the source of the chart data, in JSON (CC0).
- [romainsimon/paperasse](https://github.com/romainsimon/paperasse): a broader skill on French accounting, tax and invoicing (VAT, tax return package, e-invoicing). This repository is narrower: embedded chart of accounts, trial balance and FEC checks, closing.

## Limitations

- The data comes from arrhes/PCG, built from the ANC texts (see [NOTICE.md](NOTICE.md)). For a tax return package, a filing of accounts or a statutory auditor, cross-check against the ANC regulation in force.
- The usual balance side of each account is an indicative marker computed by prefix, not the text of the PCG.
- The SIG formulas and the financial statement layouts are a working framework, to be aligned with the company's accounting system (base, condensed, developed).
- No tax advice: corporate tax rates, VAT regimes and tax return forms change every year and are not hard-coded in the skill.
- The skill covers neither sector-specific charts (associations, insurers) nor IFRS.
- The output is preparatory work and must be validated by a qualified accountant.

## Sources for the 2025 reform

Summary drawn from the [Cegid page on the new 2025 chart of accounts](https://www.cegid.com/fr/blog/nouveau-plan-comptable-2025-nouveautes-application-tpe/) and the draft regulation presented by [Legifiscal](https://www.legifiscal.fr/actualites-fiscales/3087-comptabilite-reforme-resultat-exceptionnel-suppression-transferts-charges.html), then cross-checked against the chart itself (accounts present or absent).

## License

MIT for the code and texts of this repository, see [LICENSE](LICENSE). The chart data has its own terms, see [NOTICE.md](NOTICE.md).
