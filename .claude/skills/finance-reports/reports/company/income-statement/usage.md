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
| `--asset-bundles` | no | `cdn` unless you say otherwise, so the page renders anywhere. `local` links this tree relative to `--out` and breaks once the file moves. **Use `local` while iterating** — a cdn page renders only after its tag is pushed |

The file lands at `<symbol-lower>_income-statement_<utc>.html` — for example
`googl_income-statement_20260803T173843Z.html`. Underscore between the three fields,
hyphen inside them, so the report name stays legible as one unit. **Nothing is overwritten.** A report
carries live market data, so two builds of one symbol are two different
documents, and a directory of them sorts into a history. Old builds are yours
to delete.

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
3. **Where the money stops** — the sankey, ~13 nodes over six stages,
   drawn from the same decomposition the ladder shows.
4. **The same statement as ratios** — every line as a share of revenue.
5. **What a share got** — basic and diluted EPS, share counts, the dilution gap.
6. **Does it tie?** — one row per identity, showing what it leaves over.

The ladder precedes the diagram deliberately: the numbers are the evidence and
the picture is the reading. The reconciliation comes last because it audits
everything above it, and an audit printed first is a disclaimer.

## Rules

**The ladder decomposes the subtotal the FILING carries.** Alphabet's condensed
income statement has exactly one non-operating line — XBRL
`nonoperatingincomeexpense`, 97,983 for Q2 FY2026 — and
`totalOtherIncomeExpensesNet` reproduces it to the dollar. Interest is disclosed
in the notes rather than on the face of the statement, and the feed surfaces it
correctly: interest income less interest expense equals net interest in every
period. So the statement shows interest, then a derived remainder, then the
subtotal, and each row sums into the one below it.

**`nonOperatingIncomeExcludingInterest` is not used.** It is computed by the feed
rather than filed, and computed wrongly. GOOGL Q2 FY2026:

```
filed (XBRL nonoperatingincomeexpense)   +97,983
totalOtherIncomeExpensesNet              +97,983   agrees
nonOperatingIncomeExcludingInterest      -98,244   sign reversed
                                                   98,244 - 261 = 97,983 exactly
```

The identity holds in four of GOOGL's five quarters and **five of five for
MSFT**, so this is systemic in the feed rather than one bad company record. The
field is disclosed once, in the basis, and appears nowhere else on the page.

**Two earlier designs died here and both are worth remembering.** The first drew
the residual as its own sankey ribbon — which measured the feed's bug rather
than the filing, and at 195,438 made the diagram undrawable for one of the most
profitable companies there is. The second printed the broken field in the ladder
beside an "Unreconciled" row whose only job was to measure how wrong its
neighbour was, plus a warning callout to explain the pair. Two rows that between
them said nothing about the company. Deleting the cause deleted all three.

**One row is derived, and the basis names it.** The basis used to promise "every
line is as published and none is derived", and that promise is exactly what made
printing a broken published field feel obligatory. It was worth less than the
accuracy it cost. A derived number that ties beats a published one that does
not — but only if the page says which is which.

**An identity that cannot fail is not an audit.** The reconciliation row that
measured the removed field went with it, because it would now tie by
construction in every period.

**The exhibit shows its terms, not a verdict.** Three shapes were tried. One
residual per identity per period rendered forty zeros and the validator called
it an 88% blank section. Ticks fixed the blankness by removing every number —
thirty-five ticks and not one figure, so nothing could be checked and nothing
could be learnt. Now each identity stacks its terms vertically and lands on the
remainder, per period, which is what a tick was asserting all along.

It restates numbers the ladder already carries, deliberately: a reconciliation
a reader must cross-reference is one they will not perform, and the exhibit
exists to be performed.

**Every identity ties for GOOGL, including the interest one.** Q4 FY2025 prints
interest income of -3,127 and interest expense of +438, which look scrambled —
but they are scrambled consistently, and -3,127 - (-438) - (-2,689) is 0. Odd
signs are not the same finding as a broken identity, and the exhibit now shows
the terms, so a reader can see which of the two they are looking at.

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
