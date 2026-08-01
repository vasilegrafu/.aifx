# Components — catalogue

_Every component, by what it is for. **Generated** from the `{# purpose: … #}`_
_header of each `component.html.j2` — do not edit; run `python components/catalog_builder.py`._

109 components in 5 categories. Narrow to a candidate here, then read its `usage.md`
for the rules and its parameters. The macro name is the folder name with hyphens
turned to underscores; a view calls it as `c.<macro>(...)`.

[foundational](#foundational) 53 · [charts](#charts) 21 · [domain-specific](#domain-specific) 33 · [diagrams](#diagrams) 1 · [math](#math) 1


## foundational

Any document may use these. Nothing here knows a discipline.

| component | macro | what it is for | docs |
|---|---|---|---|
| `acceptance-criteria` | `acceptance_criteria` | Given/When/Then acceptance test for a requirement | [usage](foundational/blocks/acceptance-criteria/usage.md) |
| `appendices` | `appendices` | wrapper isolating appendix lettering from body numbering | [usage](foundational/front-back-matter/appendices/usage.md) |
| `appendix` | `appendix` | one lettered appendix section | [usage](foundational/front-back-matter/appendix/usage.md) |
| `approval-block` | `approval_block` | sign-off table of names and roles | [usage](foundational/blocks/approval-block/usage.md) |
| `badge` | `badge` | inline status/verdict pill | [usage](foundational/blocks/badge/usage.md) |
| `bridge` | `bridge` | waterfall bridge decomposing how a total moved from one value to another | [usage](foundational/blocks/bridge/usage.md) |
| `bullets` | `bullets` | unordered list for parallel, unranked points | [usage](foundational/lists/bullets/usage.md) |
| `callout` | `callout` | attention block: note/warning/decision/risk | [usage](foundational/callouts/callout/usage.md) |
| `card` | `card` | titled bordered surface that groups components; the cell unit for columns/grid | [usage](foundational/layout/card/usage.md) |
| `change-history` | `change_history` | versioned revision log for the cover | [usage](foundational/blocks/change-history/usage.md) |
| `checklist` | `checklist` | status checklist: done/pending/blocked | [usage](foundational/lists/checklist/usage.md) |
| `code` | `code` | plain preformatted code | [usage](foundational/content/code/usage.md) |
| `code-block` | `code_block` | framed code with title bar and runtime syntax coloring | [usage](foundational/content/code-block/usage.md) |
| `cohort-table` | `cohort_table` | cohort retention or vintage performance: cohorts down, periods since start across | [usage](foundational/content/cohort-table/usage.md) |
| `collapsible` | `collapsible` | click-to-expand details block | [usage](foundational/content/collapsible/usage.md) |
| `column` | `column` | one cell inside columns; span>1 makes it proportionally wider | [usage](foundational/layout/column/usage.md) |
| `columns` | `columns` | lay components side by side in a responsive row (wraps/stacks when narrow) | [usage](foundational/layout/columns/usage.md) |
| `comparison-table` | `comparison_table` | feature yes/no/partial comparison grid | [usage](foundational/content/comparison-table/usage.md) |
| `composite-score` | `composite_score` | a formula-based composite score with its inputs, the result, and the band it falls in | [usage](foundational/blocks/composite-score/usage.md) |
| `expected-value` | `expected_value` | probability-weighted scenarios with the expected value total | [usage](foundational/content/expected-value/usage.md) |
| `facts` | `facts` | key/value definition list | [usage](foundational/lists/facts/usage.md) |
| `figure` | `figure` | captioned image with alt text | [usage](foundational/content/figure/usage.md) |
| `footnotes` | `footnotes` | numbered footnotes list with back-links | [usage](foundational/front-back-matter/footnotes/usage.md) |
| `funnel` | `funnel` | nested magnitudes narrowing to a target — market sizing, or a conversion funnel | [usage](foundational/blocks/funnel/usage.md) |
| `glossary` | `glossary` | defined-terms list | [usage](foundational/blocks/glossary/usage.md) |
| `grid` | `grid` | auto-fit grid of equal tiles; min sets the smallest tile width | [usage](foundational/layout/grid/usage.md) |
| `heatmap` | `heatmap` | value grid with colour-graded cells — monthly returns, correlations, sector by region | [usage](foundational/blocks/heatmap/usage.md) |
| `kpi-tiles` | `kpi_tiles` | row of headline metric tiles with trend | [usage](foundational/blocks/kpi-tiles/usage.md) |
| `lead` | `lead` | emphasised executive-summary opening paragraph | [usage](foundational/structure/lead/usage.md) |
| `metadata-header` | `metadata_header` | report cover: the report-type kicker and the title | [usage](foundational/structure/metadata-header/usage.md) |
| `meter` | `meter` | labeled progress/target bar | [usage](foundational/blocks/meter/usage.md) |
| `metric-trend` | `metric_trend` | one metric per row across reporting periods, with CAGR and direction | [usage](foundational/content/metric-trend/usage.md) |
| `numbered` | `numbered` | ordered list where sequence matters | [usage](foundational/lists/numbered/usage.md) |
| `prose` | `prose` | body-text paragraph wrapper | [usage](foundational/structure/prose/usage.md) |
| `quadrant-map` | `quadrant_map` | 2x2 positioning map with items placed by two scores | [usage](foundational/blocks/quadrant-map/usage.md) |
| `quote` | `quote` | pull quote with attribution | [usage](foundational/content/quote/usage.md) |
| `references` | `references` | numbered, anchorable reference list | [usage](foundational/front-back-matter/references/usage.md) |
| `requirement` | `requirement` | numbered requirement card with priority and fit criterion | [usage](foundational/blocks/requirement/usage.md) |
| `revision-note` | `revision_note` | inline dated note about a change | [usage](foundational/blocks/revision-note/usage.md) |
| `risk-matrix` | `risk_matrix` | 5x5 probability-by-impact heat grid of risks | [usage](foundational/blocks/risk-matrix/usage.md) |
| `roll-forward` | `roll_forward` | movement schedule: opening balance, the movements, closing balance | [usage](foundational/content/roll-forward/usage.md) |
| `scorecard` | `scorecard` | weighted multi-criteria score with per-criterion rating bar and weighted total | [usage](foundational/blocks/scorecard/usage.md) |
| `section` | `section` | top-level anchored section: heading plus body | [usage](foundational/structure/section/usage.md) |
| `sensitivity-table` | `sensitivity_table` | two-way sensitivity grid: one output across two assumptions, base case marked | [usage](foundational/content/sensitivity-table/usage.md) |
| `steps` | `steps` | numbered procedure steps | [usage](foundational/lists/steps/usage.md) |
| `subsection` | `subsection` | nested subsection: heading plus body | [usage](foundational/structure/subsection/usage.md) |
| `table` | `table` | basic data table; wide=true to scroll horizontally | [usage](foundational/content/table/usage.md) |
| `timeline` | `timeline` | dated milestone timeline with status | [usage](foundational/blocks/timeline/usage.md) |
| `toc` | `toc` | table of contents from section ids and labels | [usage](foundational/structure/toc/usage.md) |
| `todo-marker` | `todo_marker` | inline unresolved-todo flag | [usage](foundational/callouts/todo-marker/usage.md) |
| `trace-id` | `trace_id` | anchorable traceable identifier | [usage](foundational/lists/trace-id/usage.md) |
| `variance-analysis` | `variance_analysis` | budget versus actual with the variance and whether it is favourable | [usage](foundational/content/variance-analysis/usage.md) |
| `width` | `width` | constrain any component(s) to a fixed width; optional align left/center/right | [usage](foundational/layout/width/usage.md) |

## charts

Engine-backed charts (Apache ECharts). A chart is data; a table is the same data you can read.

| component | macro | what it is for | docs |
|---|---|---|---|
| `apache-echarts` | `apache_echarts` | declarative data chart (bar/line/pie/scatter/candlestick…) via Apache ECharts, view-time SVG | [usage](charts/apache-echarts/usage.md) · [showcase](charts/apache-echarts/showcase.html) |
| `area` | `area` | a measure over time with the region beneath filled — magnitude, not just direction | [usage](charts/area/usage.md) · [showcase](charts/area/showcase.html) |
| `bar` | `bar` | a measure across categories — the workhorse comparison | [usage](charts/bar/usage.md) · [showcase](charts/bar/showcase.html) |
| `bar-negative` | `bar_negative` | a measure that crosses zero — variance, surprise, contribution | [usage](charts/bar-negative/usage.md) · [showcase](charts/bar-negative/showcase.html) |
| `correlation-matrix` | `correlation_matrix` | pairwise relationships across a set — a heatmap on the sequential ramp, not the categorical palette | [usage](charts/correlation-matrix/usage.md) · [showcase](charts/correlation-matrix/showcase.html) |
| `drawdown-curve` | `drawdown_curve` | peak-to-trough decline over time — the shape of the losing periods, not the gains | [usage](charts/drawdown-curve/usage.md) · [showcase](charts/drawdown-curve/showcase.html) |
| `funnel-chart` | `funnel_chart` | stage-to-stage narrowing — a rendered funnel with proportional bands | [usage](charts/funnel-chart/usage.md) · [showcase](charts/funnel-chart/showcase.html) |
| `gauge` | `gauge` | one value against a range — a dial, for a single bounded measure | [usage](charts/gauge/usage.md) · [showcase](charts/gauge/showcase.html) |
| `line` | `line` | a measure over time — the default form for anything with a date axis | [usage](charts/line/usage.md) · [showcase](charts/line/showcase.html) |
| `pie` | `pie` | composition of a single whole — a donut, for a handful of parts | [usage](charts/pie/usage.md) · [showcase](charts/pie/showcase.html) |
| `price-history` | `price_history` | price action over time — candlestick with volume beneath, one shared time axis | [usage](charts/price-history/usage.md) · [showcase](charts/price-history/showcase.html) |
| `radar` | `radar` | several attributes of a few entities at once — profile shape, not precise values | [usage](charts/radar/usage.md) · [showcase](charts/radar/showcase.html) |
| `sankey` | `sankey` | flow decomposition — how a total splits, merges or converts across stages | [usage](charts/sankey/usage.md) · [showcase](charts/sankey/showcase.html) |
| `scatter` | `scatter` | two measures per entity — where the relationship between them is the finding | [usage](charts/scatter/usage.md) · [showcase](charts/scatter/showcase.html) |
| `smoothed-line` | `smoothed_line` | a measure over time drawn as a smooth curve — trend over tick-by-tick detail | [usage](charts/smoothed-line/usage.md) · [showcase](charts/smoothed-line/showcase.html) |
| `stacked-area` | `stacked_area` | parts summing to a whole over time — composition and total in one figure | [usage](charts/stacked-area/usage.md) · [showcase](charts/stacked-area/showcase.html) |
| `stacked-column` | `stacked_column` | parts summing to a whole across categories — vertical stacked bars | [usage](charts/stacked-column/usage.md) · [showcase](charts/stacked-column/showcase.html) |
| `stacked-horizontal-bar` | `stacked_horizontal_bar` | parts summing to a whole, laid on their side — for long category names | [usage](charts/stacked-horizontal-bar/usage.md) · [showcase](charts/stacked-horizontal-bar/showcase.html) |
| `stacked-line` | `stacked_line` | several series summed at each point, drawn as lines — the total and its parts | [usage](charts/stacked-line/usage.md) · [showcase](charts/stacked-line/showcase.html) |
| `stacked-normalized` | `stacked_normalized` | each category as 100% — composition when the shares matter and the totals do not | [usage](charts/stacked-normalized/usage.md) · [showcase](charts/stacked-normalized/showcase.html) |
| `waterfall` | `waterfall` | how a total became another total — a bridge of additive steps | [usage](charts/waterfall/usage.md) · [showcase](charts/waterfall/showcase.html) |

## domain-specific

One analysis discipline owns these — fundamental-analysis, portfolio, macro. Classes are namespaced after the directory that owns them (`fa-`, `portfolio-`, `macro-`).

| component | macro | what it is for | docs |
|---|---|---|---|
| `aging-schedule` | `aging_schedule` | receivables or payables split into ageing buckets, with the overdue share | [usage](domain-specific/fundamental-analysis/aging-schedule/usage.md) |
| `attribution` | `attribution` | Brinson attribution: allocation effect, selection effect and their total by segment | [usage](domain-specific/portfolio/attribution/usage.md) |
| `balance-sheet` | `balance_sheet` | multi-period balance sheet with an explicit assets = liabilities + equity check | [usage](domain-specific/fundamental-analysis/balance-sheet/usage.md) |
| `capital-allocation` | `capital_allocation` | where operating cash went — capex, M&A, dividends, buybacks, debt — as a share of it | [usage](domain-specific/fundamental-analysis/capital-allocation/usage.md) |
| `cash-flow-statement` | `cash_flow_statement` | multi-period cash flow statement with an explicit free-cash-flow derivation | [usage](domain-specific/fundamental-analysis/cash-flow-statement/usage.md) |
| `catalyst-timeline` | `catalyst_timeline` | dated catalysts ahead, with expected direction and likelihood | [usage](domain-specific/fundamental-analysis/catalyst-timeline/usage.md) |
| `covenant-table` | `covenant_table` | financial covenants: the test, the limit, the actual level, and the headroom | [usage](domain-specific/fundamental-analysis/covenant-table/usage.md) |
| `cycle-position` | `cycle_position` | where the economy or a market sits in a multi-phase cycle | [usage](domain-specific/macro/cycle-position/usage.md) |
| `dcf-summary` | `dcf_summary` | discounted cash flow build: projected flows, terminal value, enterprise and equity value | [usage](domain-specific/fundamental-analysis/dcf-summary/usage.md) |
| `debt-maturity` | `debt_maturity` | the maturity wall: debt falling due by period, with coupon and share of total | [usage](domain-specific/fundamental-analysis/debt-maturity/usage.md) |
| `drawdown-table` | `drawdown_table` | the worst drawdowns with peak, trough, recovery and how long each took | [usage](domain-specific/portfolio/drawdown-table/usage.md) |
| `dupont` | `dupont` | return on equity or capital decomposed into its multiplicative drivers across periods | [usage](domain-specific/fundamental-analysis/dupont/usage.md) |
| `earnings-surprise` | `earnings_surprise` | reported versus consensus for one earnings print, with the surprise | [usage](domain-specific/fundamental-analysis/earnings-surprise/usage.md) |
| `exposure-bars` | `exposure_bars` | allocation breakdown as labeled percentage bars — sector, geography, asset class | [usage](domain-specific/portfolio/exposure-bars/usage.md) |
| `five-forces` | `five_forces` | Porter's five forces, each rated from the incumbent's point of view with its evidence | [usage](domain-specific/fundamental-analysis/five-forces/usage.md) |
| `footnote-disclosures` | `footnote_disclosures` | the numbered accounting disclosures that statement lines cite, with the ones that matter flagged | [usage](domain-specific/fundamental-analysis/footnote-disclosures/usage.md) |
| `holdings-table` | `holdings_table` | portfolio positions with a weight bar, plus whatever columns the review needs | [usage](domain-specific/portfolio/holdings-table/usage.md) |
| `income-statement` | `income_statement` | multi-period income statement: the revenue-to-net-income ladder with margin lines | [usage](domain-specific/fundamental-analysis/income-statement/usage.md) |
| `macro-indicators` | `macro_indicators` | economic indicators with latest, prior, consensus, surprise and direction | [usage](domain-specific/macro/macro-indicators/usage.md) |
| `ownership-table` | `ownership_table` | who owns the company: top holders, stake, and recent change | [usage](domain-specific/fundamental-analysis/ownership-table/usage.md) |
| `peer-comparison` | `peer_comparison` | the subject against named peers across chosen metrics, subject row highlighted | [usage](domain-specific/fundamental-analysis/peer-comparison/usage.md) |
| `performance-table` | `performance_table` | returns across periods for the portfolio, its benchmark and the excess | [usage](domain-specific/portfolio/performance-table/usage.md) |
| `recommendation` | `recommendation` | the investment call: action, price target, upside, horizon and conviction | [usage](domain-specific/fundamental-analysis/recommendation/usage.md) |
| `risk-metrics` | `risk_metrics` | risk and return statistics side by side with the benchmark | [usage](domain-specific/portfolio/risk-metrics/usage.md) |
| `security-header` | `security_header` | identity strip for the security under analysis: ticker, name, key market data | [usage](domain-specific/fundamental-analysis/security-header/usage.md) |
| `segment-reporting` | `segment_reporting` | revenue by segment with each segment's share and growth — and its profit where the source discloses it | [usage](domain-specific/fundamental-analysis/segment-reporting/usage.md) |
| `stress-test` | `stress_test` | portfolio or company impact under named stress scenarios | [usage](domain-specific/portfolio/stress-test/usage.md) |
| `thesis-pillars` | `thesis_pillars` | the load-bearing arguments of a thesis: claim, evidence, and what would break it | [usage](domain-specific/fundamental-analysis/thesis-pillars/usage.md) |
| `trade-log` | `trade_log` | dated trades with side, size, price, result and the rationale that justified them | [usage](domain-specific/portfolio/trade-log/usage.md) |
| `unit-economics` | `unit_economics` | customer unit economics: acquisition cost, lifetime value, payback and the ratio | [usage](domain-specific/fundamental-analysis/unit-economics/usage.md) |
| `valuation-multiples` | `valuation_multiples` | each valuation multiple against peer median and its own history, with the premium | [usage](domain-specific/fundamental-analysis/valuation-multiples/usage.md) |
| `valuation-range` | `valuation_range` | valuation ranges by method with the current price marked — the football field | [usage](domain-specific/fundamental-analysis/valuation-range/usage.md) |
| `working-capital` | `working_capital` | working capital efficiency: days sales, inventory and payables, and the cash conversion cycle | [usage](domain-specific/fundamental-analysis/working-capital/usage.md) |

## diagrams

The diagram subsystem: a shared viewport and one engine.

| component | macro | what it is for | docs |
|---|---|---|---|
| `mermaid` | `mermaid` | interactive Mermaid diagram: pan, zoom, live editor | [usage](diagrams/mermaid/usage.md) |

## math

The formula subsystem: KaTeX, with a readable-LaTeX fallback.

| component | macro | what it is for | docs |
|---|---|---|---|
| `formula` | `formula` | LaTeX math block, rendered by KaTeX at view time | [usage](math/formula/usage.md) |
