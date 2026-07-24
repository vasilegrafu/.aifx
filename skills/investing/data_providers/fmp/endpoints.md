# FMP endpoints — what works, what is gated, what lies

Base: `https://financialmodelingprep.com/stable`

## The MCP tool's endpoint names are NOT the API's paths

Anyone who explored FMP through the `MyFMP` MCP tool first will reach for the
names it uses. Two of them 404 against the real API:

| MCP tool name | actual path |
|---|---|
| `cashflow-statement` | **`cash-flow-statement`** |
| `profile-symbol` | **`profile`** |

The rest match: `income-statement`, `balance-sheet-statement`, `key-metrics`,
`financial-scores`, `revenue-product-segmentation`, `quote`. A wrong name
returns HTTP 404, which reads identically to a gated endpoint — so check this
table before concluding the plan is the problem.

## Plan gating (Starter)

Discovered the hard way; check here before assuming an endpoint is broken.

| endpoint | Starter |
|---|---|
| `income-statement`, `balance-sheet-statement`, `cashflow-statement` — **annual** | works |
| the same three — **quarter** | works |
| `income-statements-ttm`, `balance-sheet-statements-ttm`, `cashflow-statements-ttm` | **gated** (Ultimate/Enterprise) |
| `revenue-product-segmentation` — **annual** | works |
| `revenue-product-segmentation` — **quarter** | **gated** |
| `key-metrics`, `metrics-ratios`, `financial-scores`, `enterprise-values` | works |
| `profile-symbol`, `quote`, `peers` | works |

A gated endpoint returns an HTTP error, which `FmpClient` turns into an
`FmpError` naming this file. It does **not** return empty data, so a gated
endpoint can never be mistaken for a company with no such disclosure.

## Traps that cost real time

**TTM is not available, so build it yourself.** The first Apple profile used
FY2025 annual figures while FY2026 Q2 had already been reported — TTM revenue
was 8.5% higher than the document claimed. With the TTM endpoints gated, a
trailing figure must be summed from four `period=quarter` statements. Never let
an annual figure stand in for a trailing one without labelling it.

**`limit` silently truncates a derivation.** Pulling `cashflow-statement` with
`limit=2` and then needing five years of free cash flow forces a
back-calculation from `enterpriseValue / evToFreeCashFlow`. That reproduces the
reported number exactly, which is precisely what makes it dangerous — it looks
like a read, not a reconstruction. Pull the years you intend to show.

**`financial-scores` uses its own inputs.** Its `altmanZScore` is computed with
its own `marketCap` and `ebit`, which differ from the ones on `key-metrics` and
`income-statement` for the same fiscal year. ORCL FY2026: this endpoint returns
1.5554 (market cap 362,536, EBIT 24,153) while the same formula over
`income-statement` EBIT 24,194 and a 23 July market cap of 345,772 gives 1.51.
Neither is wrong; they are as-of different moments. State which you used.

**Statement lines do not always sum to their own subtotals.** ORCL FY2026:
`grossProfit - researchAndDevelopmentExpenses - sellingGeneralAndAdministrativeExpenses
- operatingIncome` = 2,916 against a stated `otherExpenses` of 2,923 — a $7M
gap. Likewise the financing subtotal exceeds the sum of its components by $96M.
Any diagram that must conserve needs a named, disclosed plug; it must never be
hidden inside a legitimate line.

**Currency.** `reportedCurrency` is per-statement. Nothing here converts.

## The eight `financial-profile` uses

```python
("income-statement",             {"period": "annual", "limit": 5}),
("balance-sheet-statement",      {"period": "annual", "limit": 2}),
("cashflow-statement",           {"period": "annual", "limit": 5}),
("revenue-product-segmentation", {"period": "annual"}),
("key-metrics",                  {"period": "annual", "limit": 5}),
("financial-scores",             {}),
("profile-symbol",               {}),
("quote",                        {}),
```

Peers add one `key-metrics` call each.
