# -*- coding: utf-8 -*-
"""income-statement — one statement, read all the way down, and drawn.

`financial-profile` shows the income statement as ONE exhibit among seven, at
the coarse grain that leaves room for cash, position and peers. This report does
the opposite: one statement, every line the source publishes, and a flow diagram
detailed enough to see where the money actually stops.

WHAT MAKES THIS REPORT DIFFERENT FROM ITS SANKEY IN financial-profile:

    financial-profile   11 nodes, one non-operating ribbon, annual or quarterly
                        by exhibit, and the statement is context for the rest
    income-statement    ~14 nodes, non-operating DECOMPOSED into interest
                        income, interest expense and other, and a reconciliation
                        exhibit for what the source does not tie

THE STATEMENT DECOMPOSES THE SUBTOTAL THE FILING CARRIES. A condensed income
statement has exactly ONE non-operating line -- GOOGL Q2 FY2026 tags
`nonoperatingincomeexpense` at 97,983 and stops -- and
`totalOtherIncomeExpensesNet` reproduces it to the dollar. Interest sits in the
notes, and the feed surfaces it correctly. So: interest income, interest
expense, net interest, a DERIVED remainder, then the subtotal, each row summing
into the one below it.

`nonOperatingIncomeExcludingInterest` IS NOT USED. It is computed by the feed
rather than filed, and computed wrongly:

    filed (XBRL nonoperatingincomeexpense)   +97,983
    totalOtherIncomeExpensesNet              +97,983   agrees
    nonOperatingIncomeExcludingInterest      -98,244   sign reversed
                                                       98,244 - 261 = 97,983

Four of GOOGL's five quarters and five of five for MSFT, so this is systemic in
the feed, not one bad record. It is disclosed once in the basis and appears
nowhere else. Printing it cost two designs: drawn as a sankey ribbon it measured
the feed's bug and made the diagram undrawable, and printed in the ladder it
needed a companion "Unreconciled" row to measure how wrong it was -- two rows
that between them said nothing about the company. See endpoints.md, "Statement
lines do not always sum to their own subtotals".

WHAT IS ASSERTED AND WHAT IS DISCLOSED. Anything the diagram depends on to
conserve is an assertion and stops the build. Anything the SOURCE gets wrong is
disclosed on the page, because a report that refuses to render a real filing is
useless. The line between them is the difference between "this code is broken"
and "this filing is odd".

D&A AND EBITDA ARE MEMO LINES, NEVER RIBBONS. Depreciation sits inside cost of
revenue and inside operating expenses; drawing it as its own flow would count it
twice and the diagram would still balance, because both copies are real numbers.
They appear in the ladder, under a memo heading, and nowhere in the picture.

UNITS. FMP reports raw dollars. Everything here is $ millions, converted once in
`_m()`, so no downstream number is ever in the wrong scale.
"""

import math
import sys
from datetime import date, datetime
from pathlib import Path

# Skill root on sys.path by marker, so the base imports PACKAGE-QUALIFIED.
_SKILL_DIR = next(p for p in Path(__file__).resolve().parents
                  if (p / "_paths.py").exists())
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from service_providers.fmp import FmpClient       # noqa: E402

# --------------------------------------------------------------------------
# the data appetite, declared in one place
# --------------------------------------------------------------------------
#
# THREE CALLS. The statement itself carries every line this report draws, so
# there is nothing to join and nothing to reconcile across endpoints. `profile`
# names the company and `quote` prices it, both for the cover only. Compare
# financial-profile's ~13: the cost of a report is the number of questions it
# asks, and this one asks about a single statement.
ENDPOINTS = [
    ("profile", {}),
    ("quote",   {}),
]

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _m(v):
    """Raw dollars to $ millions, as an int. One conversion point."""
    return int(round((v or 0) / 1e6))


def _chron(rows):
    """FMP returns newest-first. Everything downstream reads left-to-right."""
    return list(reversed(rows))


def _cagr(first, last, years):
    if first is None or last is None or first <= 0 or last <= 0 or not years:
        return "n/m"
    return 100 * ((last / first) ** (1 / years) - 1)


def _arrow(v):
    if not isinstance(v, (int, float)):
        return "flat"
    return "up" if v > 0.005 else ("down" if v < -0.005 else "flat")


def _label(row, basis):
    """The period label. Annual statements have no quarter to name."""
    return (f"FY{row['fiscalYear']}" if basis == "annual"
            else f"{row['period']} FY{row['fiscalYear']}")


def _nonfinite(value, path="d"):
    """Every path in a nested structure holding a NaN or an infinity.

    Reports nest: a number lives in a row, inside a list, under a key. A flat
    check would miss all of them, and the one that reaches the page is fatal
    rather than merely wrong."""
    if isinstance(value, float) and not math.isfinite(value):
        return [f"{path}={value}"]
    if isinstance(value, dict):
        return [hit for key, item in value.items()
                for hit in _nonfinite(item, f"{path}.{key}")]
    if isinstance(value, (list, tuple)):
        return [hit for i, item in enumerate(value)
                for hit in _nonfinite(item, f"{path}[{i}]")]
    return []


from reports._report_controller import ReportController    # noqa: E402

# --------------------------------------------------------------------------
# the controller
# --------------------------------------------------------------------------

class IncomeStatementReportController(ReportController):
    """One income statement, every published line, and the flow that produced
    the bottom line."""

    TITLE = "Income Statement"

    #: The sections report.html.j2 declares, in its order. Written out rather
    #: than read back from the view, so a section that silently stops rendering
    #: is a finding on the page instead of an expectation quietly agreeing with
    #: whatever happened.
    SECTIONS = ("basis", "ladder", "flow", "margins", "per-share",
                "reconciliation")

    #: A company report, so its exhibits are the fundamental-analysis family.
    PREFIX = "fa-"

    def _expected_text(self, symbol, basis, periods):
        """The subject must appear in the finished page. There is no peer group
        here, so the symbol is the whole expectation."""
        return [symbol.upper()]

    def _add_args(self, parser):
        """`--basis` is required and `--periods` is not, and the difference is
        editorial weight.

        THE BASIS CHANGES WHAT THE DOCUMENT SAYS. An annual ladder and a
        quarterly one describe different things, and a reader who assumes the
        wrong one misreads every number on the page — so it is stated out loud,
        the way `--peers` is on financial-profile.

        THE COLUMN COUNT DOES NOT. Five periods is a convention about how wide
        a table should be, not a claim about the company, and defaulting it
        costs a reader nothing."""
        parser.add_argument("symbol", help="ticker, e.g. QCOM")
        parser.add_argument("--basis", required=True,
                            choices=("annual", "quarter"),
                            help="annual or quarterly statements. Required and "
                                 "with no default: the two describe different "
                                 "things and every number on the page depends "
                                 "on which was asked for.")
        parser.add_argument("--periods", type=int, default=5,
                            help="how many periods to show, newest last "
                                 "(default 5). One call whatever the number.")

    def _fetch(self, symbol, basis, periods):
        """Live, in one pass, uncached. 3 calls.

        One statement call carrying every period, plus the two the cover needs.
        Nothing is joined across endpoints, so nothing can disagree."""
        symbol = symbol.upper()
        client = FmpClient()
        payloads = client.get_many(
            [(endpoint, dict(symbol=symbol, **params))
             for endpoint, params in ENDPOINTS])
        payloads["income-statement"] = client.get(
            "income-statement", symbol=symbol, period=basis,
            limit=max(int(periods), 2))
        payloads["_symbol"] = symbol
        payloads["_basis"] = basis
        payloads["_fetched"] = datetime.now().isoformat(timespec="seconds")
        return payloads

    def _build_context(self, p):                     # noqa: C901 — one long, flat derivation
        basis = p["_basis"]
        rows = _chron(p["income-statement"])
        profile = p["profile"][0]
        quote = p["quote"][0]
        symbol = p.get("_symbol", profile["symbol"])
        company = profile.get("companyName", symbol)

        periods = [_label(r, basis) for r in rows]
        latest = rows[-1]
        n = len(rows)

        # ------------------------------------------------------- the line items
        # Every published line, in $ millions, for every period. Read once into
        # a column-per-period dict so the ladder, the margins and the sankey are
        # all fed from the SAME numbers rather than three separate reads.
        def col(key):
            return [_m(r.get(key)) for r in rows]

        rev = col("revenue")
        cogs = col("costOfRevenue")
        gross = col("grossProfit")
        rd = col("researchAndDevelopmentExpenses")
        sm = col("sellingAndMarketingExpenses")
        ga = col("generalAndAdministrativeExpenses")
        sga = col("sellingGeneralAndAdministrativeExpenses")
        other_ex = col("otherExpenses")
        opex = col("operatingExpenses")
        opinc = col("operatingIncome")
        int_inc = col("interestIncome")
        int_exp = col("interestExpense")
        net_int = col("netInterestIncome")
        nonop = col("nonOperatingIncomeExcludingInterest")
        other_net = col("totalOtherIncomeExpensesNet")
        pretax = col("incomeBeforeTax")
        tax = col("incomeTaxExpense")
        cont = col("netIncomeFromContinuingOperations")
        disc = col("netIncomeFromDiscontinuedOperations")
        adj = col("otherAdjustmentsToNetIncome")
        net = col("netIncome")
        deductions = col("netIncomeDeductions")
        bottom = col("bottomLineNetIncome")
        dna = col("depreciationAndAmortization")
        ebitda = col("ebitda")
        ebit = col("ebit")

        # IS THE SG&A SPLIT DISCLOSED? QCOM publishes zero for both halves and
        # the combined line for the total; others publish the split. Neither is
        # an error, so the ladder and the sankey follow the filing rather than
        # printing two zero rows that read as "they spent nothing on selling".
        sga_split = all(sm[i] + ga[i] == sga[i] and sga[i] > 0 for i in range(n))

        # ------------------------------------------------- what must hold
        # These are the identities the LADDER and the DIAGRAM are built on. A
        # failure here means this code has misread the statement, not that the
        # statement is odd -- so they stop the build.
        for i, label in enumerate(periods):
            assert cogs[i] + gross[i] == rev[i], (
                f"{symbol} {label}: cost {cogs[i]} + gross {gross[i]} "
                f"!= revenue {rev[i]}")
            assert pretax[i] - tax[i] == cont[i], (
                f"{symbol} {label}: pre-tax {pretax[i]} - tax {tax[i]} "
                f"!= continuing {cont[i]}")
            assert cont[i] + disc[i] + adj[i] == net[i], (
                f"{symbol} {label}: continuing + discontinued + adjustments "
                f"!= net income {net[i]}")
            assert net[i] - deductions[i] == bottom[i], (
                f"{symbol} {label}: net {net[i]} - deductions {deductions[i]} "
                f"!= bottom line {bottom[i]}")

        # ------------------------------------------- what the SOURCE gets wrong
        # Two residuals, computed for every period and disclosed rather than
        # asserted. The operating one is usually zero; the non-operating one is
        # routinely enormous. Neither is this report's fault and neither may be
        # hidden inside a real line.
        op_resid = [gross[i] - rd[i] - sga[i] - other_ex[i] - opinc[i]
                    for i in range(n)]
        nonop_resid = [other_net[i] - (net_int[i] + nonop[i]) for i in range(n)]

        # ---------------------------------------------------------- the ladder
        def row(label, cells, kind="detail"):
            return {"label": label, "cells": cells, "kind": kind}

        ladder = [
            row("Revenue", rev, "subtotal"),
            row("Cost of revenue", cogs),
            row("Gross profit", gross, "subtotal"),
            row("Operating expenses", [], "section"),
            row("Research and development", rd),
        ]
        if sga_split:
            ladder += [row("Selling and marketing", sm),
                       row("General and administrative", ga)]
        else:
            ladder.append(row("Selling, general and administrative", sga))
        ladder += [
            row("Other operating expenses", other_ex),
            row("Total operating expenses", opex, "subtotal"),
        ]
        if any(op_resid):
            ladder.append(row("Unreconciled operating", op_resid))
        # NON-OPERATING, DECOMPOSED FROM THE SUBTOTAL THAT THE FILING CARRIES.
        # The condensed statement has exactly ONE non-operating line -- GOOGL Q2
        # FY2026 tags `nonoperatingincomeexpense` at 97,983 and stops -- and
        # `totalOtherIncomeExpensesNet` reproduces it to the dollar. Interest is
        # in the notes, and the feed surfaces it correctly: interest income less
        # interest expense equals net interest in every period, which the
        # reconciliation exhibit still checks.
        #
        # What is NOT shown here any more is the feed's own
        # `nonOperatingIncomeExcludingInterest`. It is computed, not filed, and
        # it is computed wrongly -- GOOGL published +97,983 and the field says
        # -98,244. Printing it forced a companion "Unreconciled" row whose only
        # job was to measure how wrong its neighbour was, so the statement
        # carried two rows that between them said nothing about the company.
        # Deleting the cause deleted the symptom.
        #
        # The replacement is DERIVED and labelled as derived, which is a real
        # departure for a report whose basis used to say every line is as
        # published. The basis now says which one is not, because a derived
        # number that ties beats a published one that does not.
        other_derived_col = [other_net[i] - net_int[i] for i in range(n)]
        ladder += [
            row("Operating income", opinc, "subtotal"),
            row("Non-operating", [], "section"),
            row("Interest income", int_inc),
            row("Interest expense", [-v for v in int_exp]),
            row("Net interest income", net_int, "subtotal"),
            row("Other non-operating, derived", other_derived_col),
            row("Total other income and expenses", other_net, "subtotal"),
            row("Income before tax", pretax, "subtotal"),
            row("Income tax expense", [-v for v in tax]),
            row("Net income from continuing operations", cont, "subtotal"),
        ]
        if any(disc):
            ladder.append(row("Discontinued operations", disc))
        if any(adj):
            ladder.append(row("Other adjustments", adj))
        ladder.append(row("Net income", net, "total"))
        if any(deductions):
            ladder += [row("Net income deductions", [-v for v in deductions]),
                       row("Bottom-line net income", bottom, "total")]
        ladder += [
            row("Memo — not separate cash costs", [], "section"),
            row("Depreciation and amortisation", dna),
            row("EBITDA", ebitda, "subtotal"),
            row("EBIT", ebit, "subtotal"),
        ]

        # ------------------------------------------------------------ the flow
        # LATEST PERIOD ONLY. A sankey draws one period; drawing several would
        # need one diagram each, and the ladder beside it already carries the
        # comparison.
        i = n - 1

        # A SANKEY CANNOT DRAW A LOSS, and this is not a limitation to assert
        # away. Every ribbon is a magnitude; a negative subtotal means the
        # money did not split, it ran out, and there is no honest way to draw
        # that as a width. QCOM's own Q1 FY2026 is exactly this shape -- a
        # 6,088 tax charge against 2,971 of pre-tax income, net -3,117.
        #
        # SO THE PAGE STILL RENDERS. The ladder, the margins, the per-share and
        # the reconciliation are all perfectly readable for a loss-making
        # period, and throwing the whole report away over the one exhibit that
        # cannot be drawn would be the worse answer. The section says what it
        # could not draw and why; every other section is unaffected.
        blockers = [name for name, value in (
            ("gross profit", gross[i]), ("operating income", opinc[i]),
            ("income before tax", pretax[i]), ("net income", net[i]))
            if value < 0]

        nodes = [{"name": "Revenue", "role": "source"},
                 {"name": "Cost of revenue", "role": "cost"},
                 {"name": "Gross profit", "role": "stage"},
                 {"name": "Research and development", "role": "cost"}]
        links = [{"source": "Revenue", "target": "Cost of revenue", "value": cogs[i]},
                 {"source": "Revenue", "target": "Gross profit", "value": gross[i]},
                 {"source": "Gross profit", "target": "Research and development",
                  "value": rd[i]}]

        if sga_split:
            for name, series in (("Selling and marketing", sm),
                                 ("General and administrative", ga)):
                nodes.append({"name": name, "role": "cost"})
                links.append({"source": "Gross profit", "target": name,
                              "value": series[i]})
        else:
            nodes.append({"name": "Selling, general and administrative", "role": "cost"})
            links.append({"source": "Gross profit",
                          "target": "Selling, general and administrative",
                          "value": sga[i]})

        for name, value in (("Other operating", other_ex[i]),
                            ("Unreconciled operating", op_resid[i])):
            if value > 0:
                nodes.append({"name": name, "role": "cost"})
                links.append({"source": "Gross profit", "target": name, "value": value})

        nodes.append({"name": "Operating income", "role": "stage"})
        links.append({"source": "Gross profit", "target": "Operating income",
                      "value": opinc[i]})

        # NON-OPERATING, DECOMPOSED -- the reason this report exists. Each part
        # is drawn by SIGN: what adds to pre-tax income enters as its own source
        # node, what consumes operating income leaves as a cost. Forcing either
        # into the other direction would draw a negative ribbon, which a sankey
        # renders as nothing at all.
        #
        # ONLY QUANTITIES THAT TIE ARE DRAWN, and this cost a rebuild to learn.
        # The first version drew `nonOperatingIncomeExcludingInterest` as
        # published and made up the difference with an "unreconciled" ribbon.
        # GOOGL Q2 FY2026 shows why that was wrong: the feed reports -98,244
        # against a totalOtherIncomeExpensesNet of +97,983, and 98,244 - 261 of
        # interest expense IS 97,983 exactly -- the field's SIGN is inverted.
        # The plug was therefore not measuring the filing, it was measuring the
        # feed's bug, and at 195,438 it made the diagram undrawable for one of
        # the most profitable companies there is.
        #
        # So the diagram takes the subtotal that ties (operating income +
        # totalOther == pre-tax, asserted for every period) and derives the
        # residual line from it. The published-but-inconsistent field keeps its
        # ladder row and its reconciliation row, which is where a disagreement
        # belongs: stated as a finding, not drawn as a shape.
        other_derived = other_net[i] - (int_inc[i] - int_exp[i])
        parts = [("Interest income", int_inc[i]),
                 ("Interest expense", -int_exp[i]),
                 ("Other non-operating", other_derived)]
        parts = [(name, value) for name, value in parts if value]
        # Exact by construction now, not by luck -- the derivation above cancels.
        # Kept as an assertion anyway: "by construction" has a short half-life.
        assert sum(value for _, value in parts) == other_net[i], (
            f"{symbol}: the non-operating parts sum to "
            f"{sum(v for _, v in parts)}, not {other_net[i]}")

        drains = sum(-value for _, value in parts if value < 0)
        carried = opinc[i] - drains
        # A company whose non-operating costs exceed operating income is the
        # same problem as a loss and gets the same answer: name it, skip the one
        # exhibit, keep the page.
        if carried < 0:
            blockers.append(
                f"non-operating costs of {drains:,} exceed operating income "
                f"of {opinc[i]:,}")

        for name, value in parts:
            if value < 0:
                nodes.append({"name": name, "role": "cost"})
                links.append({"source": "Operating income", "target": name,
                              "value": -value})
        nodes.append({"name": "Income before tax", "role": "stage"})
        links.append({"source": "Operating income", "target": "Income before tax",
                      "value": carried})
        for name, value in parts:
            if value > 0:
                nodes.append({"name": name, "role": "source"})
                links.append({"source": name, "target": "Income before tax",
                              "value": value})

        # A TAX BENEFIT IS A SOURCE, NOT A NEGATIVE COST. QCOM's own Q2 FY2026
        # carries a 5,138 benefit that turns 2,232 of pre-tax income into 7,370
        # of net income. Drawn as a cost it would be a negative ribbon, which a
        # sankey renders as nothing at all -- the same rule the non-operating
        # parts follow above, applied to the one line most likely to flip.
        tail = "Net income from continuing operations" if (disc[i] or adj[i]) \
            else "Net income"
        if tax[i] >= 0:
            nodes.append({"name": "Income tax", "role": "cost"})
            links.append({"source": "Income before tax", "target": "Income tax",
                          "value": tax[i]})
            to_tail = pretax[i] - tax[i]
        else:
            nodes.append({"name": "Income tax benefit", "role": "source"})
            links.append({"source": "Income tax benefit", "target": tail,
                          "value": -tax[i]})
            to_tail = pretax[i]
        nodes.append({"name": tail, "role": "stage" if tail != "Net income" else "retained"})
        links.append({"source": "Income before tax", "target": tail, "value": to_tail})
        if tail != "Net income":
            for name, value in (("Discontinued operations", disc[i]),
                                ("Other adjustments", adj[i])):
                if value:
                    nodes.append({"name": name, "role": "source" if value > 0 else "cost"})
                    if value > 0:
                        links.append({"source": name, "target": "Net income", "value": value})
                    else:
                        links.append({"source": tail, "target": name, "value": -value})
            nodes.append({"name": "Net income", "role": "retained"})
            links.append({"source": tail, "target": "Net income",
                          "value": cont[i] - sum(-v for v in (disc[i], adj[i]) if v < 0)})

        # CONSERVATION, ASSERTED HERE BECAUSE NOTHING ELSE CAN. The macro says
        # so itself: ribbons are scaled per node, so a diagram that does not
        # balance draws perfectly and lies. Every node that is not a pure source
        # or a pure sink must pass through exactly what it received.
        terminals = {"Revenue", "Income tax benefit"} \
            | {name for name, value in parts if value > 0} \
            | {"Discontinued operations", "Other adjustments"}
        if not blockers:
            for node in nodes:
                name = node["name"]
                if name in terminals:
                    continue
                inflow = sum(l["value"] for l in links if l["target"] == name)
                outflow = sum(l["value"] for l in links if l["source"] == name)
                if inflow and outflow:
                    assert inflow == outflow, (
                        f"{symbol}: sankey node {name!r} takes {inflow} and "
                        f"passes {outflow} -- the diagram would draw and be wrong")
            for link in links:
                assert link["value"] >= 0, (
                    f"{symbol}: negative ribbon {link['source']} -> "
                    f"{link['target']} ({link['value']})")

        # The one exhibit is dropped, never the page. An empty node list is what
        # the view branches on; the reason is what it prints instead.
        flow_note = ""
        if blockers:
            nodes, links = [], []
            flow_note = (
                f"No flow diagram for {periods[-1]}: "
                + ", ".join(blockers)
                + ". A sankey ribbon is a magnitude, so a negative subtotal has "
                  "no honest width — the money did not split, it ran out. Every "
                  "other exhibit on this page covers the period normally, and "
                  "the statement above carries the same numbers.")

        # Sankey labels are drawn as CANVAS TEXT and never pass an HTML parser,
        # so "&amp;" would render as five literal characters. This report writes
        # "and" throughout for that reason; the check is what keeps it true.
        for node in nodes:
            assert "&" not in node["name"], \
                f"{symbol}: ampersand in sankey label {node['name']!r}"

        # ---------------------------------------------------------- the margins
        def pct_of_revenue(series):
            return [100 * series[k] / rev[k] if rev[k] else 0 for k in range(n)]

        def trend(label, values, fmt=None):
            delta = values[-1] - values[0]
            entry = {"label": label, "cells": [round(v, 1) for v in values],
                     "cagr": delta * 100, "cagr_fmt": "bps", "dir": _arrow(delta)}
            if fmt:
                entry["fmt"] = fmt
            return entry

        # Every margin is against REVENUE except the tax rate, which is against
        # pre-tax income -- a tax charge over revenue is a number with no
        # meaning, and putting it in the same column as the others would invite
        # exactly that reading. The label says so.
        margin_rows = [
            trend("Gross margin", pct_of_revenue(gross)),
            trend("R&D / revenue", pct_of_revenue(rd)),
            trend(("SG&A / revenue" if not sga_split else "Selling and G&A / revenue"),
                  pct_of_revenue(sga)),
            trend("Operating expenses / revenue", pct_of_revenue(opex)),
            trend("Operating margin", pct_of_revenue(opinc)),
            trend("EBITDA margin", pct_of_revenue(ebitda)),
            trend("Pre-tax margin", pct_of_revenue(pretax)),
            trend("Effective tax rate (of pre-tax income)",
                  [100 * tax[k] / pretax[k] if pretax[k] else 0 for k in range(n)]),
            trend("Net margin", pct_of_revenue(net)),
        ]

        # -------------------------------------------------------- the per-share
        eps = [r.get("eps") or 0 for r in rows]
        eps_dil = [r.get("epsDiluted") or 0 for r in rows]
        sh = [(r.get("weightedAverageShsOut") or 0) / 1e6 for r in rows]
        sh_dil = [(r.get("weightedAverageShsOutDil") or 0) / 1e6 for r in rows]
        dilution = [100 * (sh_dil[k] / sh[k] - 1) if sh[k] else 0 for k in range(n)]

        pershare_rows = [
            {"label": "Earnings per share, basic", "cells": [round(v, 2) for v in eps],
             "cagr": _cagr(eps[0], eps[-1], n - 1), "dir": _arrow(_cagr(eps[0], eps[-1], n - 1))},
            {"label": "Earnings per share, diluted", "cells": [round(v, 2) for v in eps_dil],
             "cagr": _cagr(eps_dil[0], eps_dil[-1], n - 1),
             "dir": _arrow(_cagr(eps_dil[0], eps_dil[-1], n - 1))},
        ]
        share_rows = [
            {"label": "Weighted average shares, basic", "cells": [round(v) for v in sh],
             "cagr": _cagr(sh[0], sh[-1], n - 1), "dir": _arrow(-_cagr(sh[0], sh[-1], n - 1))},
            {"label": "Weighted average shares, diluted", "cells": [round(v) for v in sh_dil],
             "cagr": _cagr(sh_dil[0], sh_dil[-1], n - 1),
             "dir": _arrow(-_cagr(sh_dil[0], sh_dil[-1], n - 1))},
            {"label": "Dilution (diluted over basic)", "cells": [round(v, 2) for v in dilution],
             "fmt": "pct", "cagr": (dilution[-1] - dilution[0]) * 100, "cagr_fmt": "bps",
             "dir": _arrow(dilution[-1] - dilution[0])},
        ]

        # ---------------------------------------------------- the reconciliation
        # EVERY IDENTITY WORKED OUT, PER PERIOD. Each block stacks the terms
        # vertically and lands on what they leave over, so a reader can follow
        # the arithmetic in the quarter they care about instead of taking a tick
        # on trust.
        #
        # THIS IS THE THIRD SHAPE. The first printed one residual per identity
        # per period and rendered forty zeros, which the validator called an 88%
        # blank section; the second replaced them with ticks, which fixed the
        # blankness by removing every number -- thirty-five ticks and not one
        # figure, so nothing could be checked and nothing could be learnt. The
        # terms themselves are the answer: they are what a tick was asserting.
        #
        # It restates numbers the ladder already shows, deliberately. A
        # reconciliation a reader has to cross-reference is one they will not
        # perform, and the whole exhibit exists to be performed.
        #
        # Reuses the income_statement component rather than a table, because its
        # section / detail / subtotal kinds map exactly onto identity name /
        # term / leftover, and the exhibit then reads in the same visual
        # language as the statement it audits.
        def recon_block(title, parts):
            """One identity: a heading, its signed terms, and the remainder.

            Terms arrive ALREADY SIGNED, so the leftover is a plain sum and the
            label carries the operator the reader sees. Deriving the sign from
            the label instead would put the arithmetic in two places."""
            rows = [{"label": title, "cells": [], "kind": "section"}]
            rows += [{"label": label, "cells": vals, "kind": "detail"}
                     for label, vals in parts]
            rows.append({"label": "= leftover", "kind": "subtotal",
                         "cells": [sum(vals[k] for _, vals in parts)
                                   for k in range(n)]})
            return rows

        def neg(values):
            return [-v for v in values]

        recon_rows = (
            recon_block("Revenue", [
                ("Cost of revenue", cogs),
                ("+ Gross profit", gross),
                ("− Revenue", neg(rev))])
            + recon_block("Operating expenses", [
                ("Research and development", rd),
                ("+ Selling, general and administrative", sga),
                ("+ Other operating expenses", other_ex),
                ("− Total operating expenses", neg(opex))])
            + recon_block("Operating income", [
                ("Gross profit", gross),
                ("− Total operating expenses", neg(opex)),
                ("− Operating income", neg(opinc))])
            + recon_block("Net interest", [
                ("Interest income", int_inc),
                ("− Interest expense", neg(int_exp)),
                ("− Net interest income", neg(net_int))])
            + recon_block("Income before tax", [
                ("Operating income", opinc),
                ("+ Total other income and expenses", other_net),
                ("− Income before tax", neg(pretax))])
            + recon_block("Continuing operations", [
                ("Income before tax", pretax),
                ("− Income tax expense", neg(tax)),
                ("− Net income from continuing operations", neg(cont))])
            + recon_block("EBIT", [
                ("EBITDA", ebitda),
                ("− Depreciation and amortisation", neg(dna)),
                ("− EBIT", neg(ebit))])
        )

        # ----------------------------------------------------------- the basis
        period_end = datetime.strptime(latest["date"], "%Y-%m-%d").date()
        filed = datetime.strptime(latest["filingDate"], "%Y-%m-%d").date()
        report_date = date.today()
        unit = "$ millions"
        basis_word = "fiscal years" if basis == "annual" else "fiscal quarters"

        d = {
            "slug": symbol.lower(),
            "title": f"{company} — Income Statement",
            "ticker": symbol,
            "company": company,
            "exchange": profile.get("exchange", ""),
            "unit": unit,
            "periods": periods,
            "period": periods[-1],
            "price_date": report_date.strftime("%d %B %Y"),
            "header_facts": [
                {"label": "Price", "value": f"${quote['price']:,.2f}"},
                {"label": "Market cap", "value": f"${_m(quote['marketCap']) / 1000:,.0f}B"},
                {"label": f"Revenue {periods[-1]}", "value": f"${rev[-1] / 1000:,.1f}B"},
                {"label": f"Net income {periods[-1]}", "value": f"${net[-1] / 1000:,.1f}B"},
                {"label": "Diluted EPS", "value": f"${eps_dil[-1]:,.2f}"},
            ],
            "basis_facts": [
                {"term": "Report date",
                 "value": f"{report_date:%d %B %Y} — every date below is measured "
                          f"against it"},
                {"term": "Basis",
                 "value": f"{n} {basis_word}, {periods[0]} to {periods[-1]}. Every "
                          f"exhibit on this page is that same series; nothing here "
                          f"mixes periods"},
                {"term": "Latest period",
                 "value": f"{periods[-1]}, ended {period_end:%d %B %Y} — "
                          f"{(report_date - period_end).days} days before this report"},
                {"term": "Filed", "value": f"{filed:%d %B %Y}"},
                {"term": "Currency and unit",
                 "value": f"{latest.get('reportedCurrency', 'USD')}, {unit} unless "
                          f"stated. Per-share figures are as reported"},
            ],
            # ladder
            "ladder_rows": ladder,
            "ladder_caption": f"{company} — income statement, {periods[0]} to {periods[-1]}",
            # flow
            "flow_nodes": nodes,
            "flow_links": links,
            "flow_note": flow_note,
            "flow_caption": f"{company} {periods[-1]} — revenue to net income, "
                            f"every published line",
            # margins / per share / reconciliation
            "margin_rows": margin_rows,
            "pershare_rows": pershare_rows,
            "share_rows": share_rows,
            "recon_rows": recon_rows,
        }
        return d

    #: Every `d.<name>` report.html.j2 reads, extracted from the view. The list
    #: is what makes the next method a CONTRACT rather than a spot check: a key
    #: the recipe stops using, or starts using, shows up here as a diff.
    READS = (
        "basis_facts", "company", "exchange", "flow_caption", "flow_links",
        "flow_nodes", "flow_note", "header_facts", "ladder_caption", "ladder_rows",
        "margin_rows", "period", "periods", "pershare_rows", "price_date",
        "recon_rows", "share_rows", "ticker",
        "unit",
    )

    def _validate_context(self, d):
        """What the VIEW needs, checked before anything is rendered.

        Distinct from the assertions in _build_context, and deliberately: those
        check the ARITHMETIC — that the ladder ties and the diagram conserves —
        and belong beside the derivation that produces them. These check the
        CONTRACT with the recipe, which the arithmetic knows nothing about."""
        missing = [key for key in self.READS if key not in d]
        assert not missing, \
            (f"income-statement: the recipe reads {len(missing)} key(s) the "
             f"controller never built: {', '.join(missing)}")

        # NaN and the infinities are float instances, so no type check sees
        # them. They travel all the way into `| tojson`, which writes them into
        # the chart's <pre> unquoted; that is not JSON, so the browser's
        # JSON.parse throws and the exhibit renders as nothing at all.
        broken = sorted(_nonfinite(d))
        assert not broken, \
            (f"income-statement: {len(broken)} non-finite number(s) would reach "
             f"the page and break JSON.parse: {', '.join(broken[:8])}"
             + (" ..." if len(broken) > 8 else ""))
