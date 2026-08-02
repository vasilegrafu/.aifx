# financial-profile

_Authoring guidance for the `financial-profile` report — what it argues, what it
needs, and what it costs. The twin of a component's `usage.md`, one level up._

Where a company's money comes from, where it goes, what it owns, and how that
shape changed. **Fully generated** — every number is fetched and derived, there
are no prose slots, and the output is a build artifact that is regenerated
rather than edited.

**Use when** the question is about one company's financial shape: its revenue
structure, its cash conversion, its balance-sheet composition, and how those
moved over five years. **Not** for a thesis, a valuation, or a market view —
this report describes, it does not argue a position.

## Build it

```bash
S=.claude/skills/finance-reports        # from the PROJECT ROOT — see ../../../SKILL.md

python $S/reports/report_builder.py financial-profile MU --peers none --out DIR
python $S/reports/report_builder.py financial-profile MU --peers INTC,WDC,STX --out DIR
python $S/reports/report_builder.py financial-profile --help
```

| argument | required | notes |
|---|---|---|
| `symbol` | yes | ticker, upper-cased for you |
| `--peers` | **yes** | tickers, or `none`. No default: choosing nobody is still choosing. One extra call each |
| `--out` | yes | no default. **Ask if you were not told it** — see below |

The file lands at `<symbol-lower>-financial-profile.html` and **overwrites**
without asking. Two symbols never collide; the same symbol twice is the same
report with newer numbers.

**Do not choose `--out` yourself.** If the destination was not given, ask for
it before running anything. A report is a deliverable, and where it lands is the
reader's decision — invent a path and the file is somewhere nobody looks, its
asset links are computed against a directory nobody chose, and ~13 API calls
have been spent producing it. One question is cheaper than any of that.

The same holds for `--peers`: see below on why it is editorial.

**Choosing peers is an editorial act.** The flag exists rather than an API call
because a peer group chosen by a screener is not a peer group. Pick companies a
reader would accept as comparable on business model, not on sector tag.

It is **required and has no default**, so there is no way to end up with a peer
group by accident. `--peers none` renders the comparison exhibit with the
subject alone in it — a legitimate answer, but one someone has to give. Choosing
nobody is still choosing.

## What it fetches

~13 calls, ~13 seconds, uncached, every build. Nothing is stored between runs.

| endpoint | period | for |
|---|---|---|
| `income-statement` | annual ×5 | trends, margins, per-share |
| `cash-flow-statement` | annual ×5 | free cash flow, per-share |
| `revenue-product-segmentation` | annual | segment mix, bridge, stacked exhibits |
| `key-metrics` | annual ×5 | per-share and peer columns |
| `financial-scores` | — | Piotroski |
| `profile`, `quote` | — | header, exchange, price date |
| `income-statement` | quarter ×2 | the revenue sankey |
| `balance-sheet-statement` | quarter ×5 | position sankey and table, YoY column |
| `cash-flow-statement` | quarter ×2 | the cash sankey |

Statements are pulled **twice on purpose**: annual for the multi-year exhibits,
quarterly for the three that describe the last reported quarter.

**Plan constraint.** On the Starter plan, `key-metrics` and
`revenue-product-segmentation` serve annual only — quarterly returns HTTP 402.
That is why every exhibit downstream of them stays annual. See
`service_providers/fmp/endpoints.md` before adding an endpoint.

**Units.** FMP reports raw dollars. Everything is converted to **$ millions
once**, in `_m()`, so no downstream number is ever in the wrong scale.

## What a reader gets

Seven sections, in the order the argument builds:

| section | exhibits |
|---|---|
| Snapshot | security header, basis facts |
| Where the money comes from | revenue sankey, segment table |
| Where the money goes | cash sankey |
| What it owns and owes | balance-sheet sankey, table, Altman Z |
| Per share | share-count roll-forward, per-share trend |
| How it evolved | segment trend, stacked area, 100% stacked, revenue bridge, margin trend |
| How it compares | peer comparison |

**3 sankeys, 5 charts, 8 tables.** Reading it top to bottom should tell you what
the report argues: what it is → where money comes from → where it goes → what it
owns → what a share owns → how that changed → how it compares.

## What is guaranteed

**13 identity assertions** in `_build_context`, and they are the reason to trust
the diagrams: a sankey scales each node's ribbons independently, so **one that
does not conserve draws perfectly and lies**. Cost + gross == revenue.
Liabilities + equity == assets. Each sankey sums to its own table. The segment
bridge reaches its endpoint. None of that is visible in the output and none of
it can be checked by a template.

**`_validate_context` checks the contract with the view**: the 47 `d.*` names
the recipe reads are all present, and no `NaN` or infinity survives anywhere in
the nested structure — those pass every type check, reach `| tojson` unquoted,
and make the browser's `JSON.parse` throw, so the exhibit renders as nothing.

A build that violates either **stops**. It does not warn.

## Rules

- **Never edit the output.** It is regenerated; your edit is lost on the next
  build and is invisible to the controller in the meantime.
- **A number a reader sees was derived here, never in the template.** The view
  chooses which exhibits appear and in what order, and does no arithmetic.
- **Adding an exhibit is two edits**: the data in `_build_context`, its name in
  `READS`, then the `c.<macro>(...)` call in `report.html.j2`.
- **Assert anything you derive that must balance.** The cost of a missing
  assertion is a confident, wrong picture.
- **A renamed segment is indistinguishable from a closed one**, and the report
  says so rather than guessing. `revenue-product-segmentation` reports a
  renamed line under both names, so a reorganisation appears as one segment at
  **−100.0%** beside a new one at **0.0%** — the second has no prior year to
  divide by. Both figures are correct and the pair reads as a collapse: INTU's
  largest business, renamed for FY2025, prints in red. When a segment vanishes
  or appears, `seg_note` states what was observed and lands under the table.
  It is **a note, not an assertion** — a segment really can be closed, and
  nothing in the data distinguishes the two.
- Requires a live network and `FMP_API_KEY` — see Credentials in `SKILL.md`.
  There is no offline mode and no cached payloads.
