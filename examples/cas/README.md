# Test cases with known closing balances

[Français](README.fr.md) | **English**

Each folder is a small fictional company with figures worked out by hand:

- `avant.csv`: trial balance **before** closing.
- `ecritures.csv`: the closing entries (same columns, added account by account).
- `attendu.json`: the expected result: totals, profit, net assets, and the balance of every account after closing.

| Case | Content | Total debit after closing (EUR) | Profit | Net assets |
|---|---|---|---|---|
| `01-societe-de-services` | Services company: depreciation, accrued expense, prepaid expense, corporate income tax | 95 200 | 10 200 | 42 700 |
| `02-commerce-stock-et-creances` | Trading company: stock variation, impairment of a receivable, accrued interest, depreciation | 141 700 | 17 500 | 62 000 |

## Check it yourself

```bash
python3 skills/pcg-france/scripts/pcg.py balance examples/cas/01-societe-de-services/avant.csv --ecritures examples/cas/01-societe-de-services/ecritures.csv
python3 -m unittest tests.test_cas -v
```

The test recomputes the figures with its own code, independently of the script, then checks that the script returns the same totals and profit. The balance sheet rule used: classes 1 to 5 with a debit balance go to assets, with a credit balance to liabilities; contra accounts (28, 29, 39, 49, 59) are netted against assets; the profit is added to liabilities.

## Limits, and a request

- The companies and figures are **invented**. They show how the skill computes; they are not a model for a real filing.
- The figures were worked out by hand and checked by code, **not reviewed by an accountant**. The choice of accounts and the closing entries are simplified (for example, no VAT settlement and no appropriation of the result).
- **If you are an accountant, I would be glad if you tested these cases and told me what you find** (wrong account, missing entry, a closing practice that differs): [open an issue](https://github.com/arnoldkouya/pcg-skill/issues) or send a pull request. Corrections are welcome and will be credited.
