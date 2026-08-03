# income-statement

_Authoring guidance for the `income-statement` report — what it argues, what it
needs, and what it costs. The twin of a component's `usage.md`, one level up._

One income statement, read all the way down: every line the source publishes,
the same statement drawn as a flow, the same statement as ratios, and an audit
of whether it ties. **Fully generated** — every number is fetched, there are no
prose slots, and the output is a build artifact that is regenerated rather than
edited.

**Use when** the question is about the statement itself — what the cost
structure is, where operating income goes before it becomes net income, how much
of the bottom line the tax line took. **Not** for a company overview: `financial-profile`
covers cash, balance sheet, segments and peers, and shows this statement at a
coarser grain as one exhibit among seven.

## Build it

```bash
S=.claude/skills/finance-reports        # from the PROJECT ROOT — see ../../../SKILL.md

python $S/reports/report_builder.py income-statement QCOM --basis quarter --out DIR
python $S/reports/report_builder.py income-statement QCOM --basis annual --periods 8 --out DIR
python $S/reports/report_builder.py income-statement QCOM --basis annual --out DIR --asset-bundles local
python $S/reports/report_builder.py income-statement --help
```

| argument | required | notes |
|---|---|---|
| `symbol` | yes | ticker, upper-cased for you |
| `--basis` | **yes** | `annual` or `quarter`. No default: the two describe different things and every number on the page depends on which was asked for |
| `--periods` | no | how many periods, newest last (default 5). One call whatever the number |
| `--out` | yes | no default. **Ask if you were not told it** |
| `--asset-bundles` | no | `cdn` unless you say otherwise, so the page renders anywhere. `local` links this tree relative to `--out` and breaks once the file moves |

The file lands at `<symbol-lower>-income-statement.html` and **overwrites**
without asking.

**Do not choose `--out` yourself.** If the destination was not given, ask before
running anything — a report is a deliverable and where it lands is the reader's
decision.

**`--basis` is editorial, `--periods` is not.** An annual ladder and a quarterly
one are different documents, and a reader who assumes the wrong one misreads
every figure — so it is stated out loud, the way `--peers` is on
`financial-profile`. A column count is a claim about table width, not about the
company, so it defaults.

## What it fetches

**3 calls**, uncached, every build. Nothing is stored between runs.

| endpoint | period | for |
|---|---|---|
| `income-statement` | `--basis`, `limit=--periods` | every exhibit on the page |
| `profile` | — | company name and exchange, for the cover |
| `quote` | — | price and market cap, for the cover |

One statement call carries every period and every line, so **nothing is joined
across endpoints and nothing can disagree**. Compare `financial-profile`'s ~13
calls: the cost of a report is the number of questions it asks, and this one
asks about a single statement.

## The exhibits, in order

1. **What this is** — cover, then the basis: which periods, whether the filing
   splits its selling costs, where depreciation is, and what does not reconcile.
2. **The statement** — the full ladder, ~24 rows, subtotals kept as published
   rather than recomputed, with a memo block for D&A, EBITDA and EBIT.
3. **Where the money stops** — the sankey, ~14 nodes over six stages.
4. **The same statement as ratios** — every line as a share of revenue.
5. **What a share got** — basic and diluted EPS, share counts, the dilution gap.
6. **Does it tie?** — one row per identity, showing what it leaves over.

The ladder precedes the diagram deliberately: the numbers are the evidence and
the picture is the reading. The reconciliation comes last because it audits
everything above it, and an audit printed first is a disclaimer.

## Rules

**The residual is drawn, not hidden.** `totalOtherIncomeExpensesNet` is what the
statement uses to get from operating income to pre-tax income, and it is **not**
the sum of the components the same payload publishes. QCOM Q3 FY2026:

```
netInterestIncome                     -81
nonOperatingIncomeExcludingInterest -1,014
                                    ------
sum of components                   -1,095
totalOtherIncomeExpensesNet         +  836
unreconciled                         1,931   ← 78% of pre-tax income
```

That is not rounding, and it is not one company: QCOM shows a gap in all five
quarters. It gets its own ladder row, its own reconciliation row and a line in
the basis. See `service_providers/fmp/endpoints.md`, *"Statement lines do not
always sum to their own subtotals"* — this report is the case that rule was
written for.

**But the residual is not drawn, and that distinction cost a rebuild.** The
first version drew `nonOperatingIncomeExcludingInterest` as published and made
up the difference with an "unreconciled" ribbon. GOOGL Q2 FY2026 shows why that
was wrong:

```
nonOperatingIncomeExcludingInterest -98,244
totalOtherIncomeExpensesNet         +97,983
interest expense                        261      98,244 - 261 = 97,983 exactly
```

The field's **sign is inverted** in the feed. The plug was therefore measuring
the feed's bug rather than the filing, and at 195,438 it made the diagram
undrawable for one of the most profitable companies there is.

**So the diagram is built only from quantities that tie.** `operating income +
totalOtherIncomeExpensesNet == income before tax` holds in every period and is
asserted, so the other-non-operating ribbon is *derived* from that subtotal. The
published-but-inconsistent field keeps its ladder row and its reconciliation
row, which is where a disagreement belongs: stated as a finding, not drawn as a
shape. A picture asserts that its parts are real; a table can say "this is what
they published and it does not add up".

**D&A and EBITDA are memo lines, never ribbons.** Depreciation sits inside cost
of revenue and inside operating expenses. Drawing it as its own flow counts it
twice, and the diagram still balances, because both copies are real numbers.
They appear in the ladder under a memo heading and nowhere in the picture.

**Undisclosed is not zero.** QCOM publishes `0` for both halves of SG&A and the
combined figure for the total. The ladder shows the combined line rather than
two zero rows, because a zero row reads as "they spent nothing on selling",
which is a different claim from "they did not break it out". The basis says
which happened.

**Assert what the diagram depends on; disclose what the source gets wrong.**
A failed assertion means this code misread the statement and the build stops. A
residual means the filing is odd, and the page says so and renders. The line
between them is the difference between "this is broken" and "this is unusual" —
a report that refuses to render a real filing is useless.

**Non-operating items are drawn by sign.** What adds to pre-tax income enters as
its own source node; what consumes operating income leaves as a cost. Forcing
either into the other direction draws a negative ribbon, which a sankey renders
as nothing at all. A company whose non-operating costs exceed operating income
cannot be drawn with this topology, and the controller says so by name rather
than emitting an invisible link.

**Conservation is asserted in the controller, never in the macro.** The sankey
scales each node's ribbons independently, so a diagram that does not balance
draws perfectly and lies. Only the controller has the arithmetic.

**Sankey labels are canvas text.** They never pass an HTML parser, so `&amp;`
renders as five literal characters. This report writes "and" throughout, and
asserts that no label contains an ampersand.
