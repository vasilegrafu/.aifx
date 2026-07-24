# -*- coding: utf-8 -*-
"""financial-profile — where a company's money comes from, where it goes, what
it owns, and how that shape changed.

THREE FUNCTIONS, THREE JOBS.

    fetch(symbol, peers)  the only thing that touches the network
    shape(payloads)       pure arithmetic; ASSERTS every identity, then returns
                          the data the recipe renders
    sample()              canned payloads so `check` runs offline

WHY THE ASSERTIONS LIVE HERE. Three of this report's exhibits are sankeys, and a
sankey scales each node's ribbons independently — so one that does not conserve
draws perfectly and lies. The same is true of a bridge whose steps do not reach
its endpoint and a balance sheet whose sankey disagrees with its own table. None
of that is visible in the output and none of it can be checked by the template,
because only this file has the arithmetic. Every identity is asserted before a
single component is called.

UNITS. FMP reports raw dollars. Everything here is $ millions, converted once in
`_m()`, so no downstream number is ever in the wrong scale.
"""

import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from data_providers.fmp import FmpClient          # noqa: E402

# --------------------------------------------------------------------------
# the data appetite, declared in one place
# --------------------------------------------------------------------------

ENDPOINTS = [
    ("income-statement",             {"period": "annual", "limit": 5}),
    ("balance-sheet-statement",      {"period": "annual", "limit": 2}),
    # limit=5, not 2. With 2 years, five years of free cash flow can only be
    # reconstructed from `enterpriseValue / evToFreeCashFlow` — which reproduces
    # the reported number exactly and therefore looks like a read rather than a
    # back-calculation. Pull the years you intend to show.
    ("cash-flow-statement",          {"period": "annual", "limit": 5}),
    ("revenue-product-segmentation", {"period": "annual"}),
    ("key-metrics",                  {"period": "annual", "limit": 5}),
    ("financial-scores",             {}),
    ("profile",                      {}),
    ("quote",                        {}),
]

# The 17 slots this report cannot fill. They render as visible prompts; the
# builder never invents an argument. Keeping them in one dict makes the count
# checkable rather than a thing someone believes.
PROSE = {
    "lead": "{{one paragraph: what the business sells, to whom, and the one "
            "structural fact about its economics a reader should carry into the rest}}",
    "income_note": "{{one sentence: where the margin is made and what consumes it}}",
    "income_prose": "{{which segment actually pays for the company — revenue share "
                    "and profit share are rarely the same number, and the gap is the point}}",
    "cash_note": "{{one sentence: what management actually did with the money}}",
    "cash_prose": "{{reinvestment versus return of capital}}",
    "position_note": "{{one sentence: equity as a share of assets, and what funds "
                     "the rest — a stock, not a flow}}",
    "score_note": "{{what the score does and does not tell you about this company}}",
    "position_prose": "{{liquidity, leverage, and what the balance sheet is FOR here}}",
    "shares_note": "{{how much of the per-share growth was bought rather than earned}}",
    "pershare_prose": "{{compare these growth rates with the totals above — the gap "
                      "IS the buyback}}",
    "stacked_note": "{{one sentence: did the whole grow, and which band grew with it}}",
    "mix_note": "{{one sentence: is this the same business it was five years ago?}}",
    "bridge_note": "{{one sentence: which segment produced the growth, and what share}}",
    "evolution_prose": "{{whether growth came with operating leverage or bought it "
                       "with spending}}",
    "peers_prose": "{{where the subject is genuinely different, and whether that "
                   "difference is an advantage or a lag}}",
    "reading": "{{the four or five sentences a reader should leave with — the shape of "
               "the earnings, the spending, the balance sheet, and what changed. "
               "State what would change this reading.}}",
    "segment_source": "{{filing and page}}",
}


def add_args(parser):
    parser.add_argument("symbol", help="ticker, e.g. ORCL")
    parser.add_argument("--peers", default="",
                        help="comma-separated tickers. A peer group chosen by an "
                             "API is not a peer group — name them deliberately.")


# --------------------------------------------------------------------------
# fetch
# --------------------------------------------------------------------------

def fetch(symbol, peers=""):
    """Live, in one pass, uncached. ~10 calls, ~10 seconds."""
    symbol = symbol.upper()
    client = FmpClient()
    payloads = client.get_many(
        [(endpoint, dict(symbol=symbol, **params)) for endpoint, params in ENDPOINTS])
    payloads["_symbol"] = symbol
    payloads["_fetched"] = datetime.now().isoformat(timespec="seconds")
    payloads["_peers"] = {}
    for peer in [p.strip().upper() for p in peers.split(",") if p.strip()]:
        payloads["_peers"][peer] = client.get("key-metrics", symbol=peer,
                                              period="annual", limit=1)
    return payloads


def sample():
    """Canned payloads for `check` — no network, no credential.

    A guard that needs a secret to run stops being run."""
    return json.loads((HERE / "sample.json").read_text(encoding="utf-8"))


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


def _fy(row):
    return f"FY{row['fiscalYear']}"


def _seg_label(name):
    """Tidy FMP's product-line labels without inventing a per-company map.

    The feed returns things like 'Cloud And License Business' — a trailing
    'Business' on every line and a capitalised 'And'. Both are noise. Stripping
    them is a generic transform that reads correctly for any issuer; anything
    beyond it (a house spelling, an abbreviation) is an editorial choice that
    belongs to whoever fills the prose, not to the data layer."""
    name = name.strip()
    if name.endswith(" Business"):
        name = name[:-len(" Business")]
    return name.replace(" And ", " and ")


# --------------------------------------------------------------------------
# shape
# --------------------------------------------------------------------------

def shape(p):                                        # noqa: C901 — one long, flat derivation
    inc = _chron(p["income-statement"])
    bs = _chron(p["balance-sheet-statement"])
    cf = _chron(p["cash-flow-statement"])
    km = _chron(p["key-metrics"])
    scores = p["financial-scores"][0]
    profile = p["profile"][0]
    quote = p["quote"][0]
    symbol = p.get("_symbol", profile["symbol"])

    years = [_fy(r) for r in inc]
    latest = inc[-1]
    bs_now, bs_prev = bs[-1], bs[-2]
    cash = cf[-1]
    km_now = km[-1]

    report_date = date.today()
    period_end = datetime.strptime(latest["date"], "%Y-%m-%d").date()
    filed = datetime.strptime(latest["filingDate"], "%Y-%m-%d").date()

    # ---------------------------------------------------------------- income
    rev = _m(latest["revenue"])
    cogs, gross = _m(latest["costOfRevenue"]), _m(latest["grossProfit"])
    rd = _m(latest["researchAndDevelopmentExpenses"])
    sga = _m(latest["sellingGeneralAndAdministrativeExpenses"])
    opinc, pretax = _m(latest["operatingIncome"]), _m(latest["incomeBeforeTax"])
    tax, net = _m(latest["incomeTaxExpense"]), _m(latest["netIncome"])
    net_cont = _m(latest["netIncomeFromContinuingOperations"])

    assert cogs + gross == rev, f"{symbol}: cost + gross != revenue ({cogs}+{gross}≠{rev})"

    # The statement does not always sum to its own subtotals. ORCL FY2026 leaves
    # a $7m gap between the expense lines and operating income. A diagram that
    # must conserve needs that gap NAMED and disclosed — never buried inside a
    # legitimate line, where it would silently misstate a real expense.
    other_opex = gross - rd - sga - opinc
    assert other_opex >= 0, (
        f"{symbol}: expense lines exceed gross profit by {-other_opex}m. This report's "
        f"income sankey assumes other operating costs are a cost; here they are income. "
        f"Extend the sankey rather than forcing the sign.")

    non_op = opinc - pretax
    nci = net_cont - net
    assert tax + nci + net == pretax, (
        f"{symbol}: tax {tax} + NCI {nci} + net {net} != pre-tax {pretax}")

    inc_nodes = [{"name": "Revenue", "role": "source"},
                 {"name": "Cost of revenue", "role": "cost"},
                 {"name": "Gross profit", "role": "stage"},
                 {"name": "Research & development", "role": "cost"},
                 {"name": "Sales, general & administrative", "role": "cost"}]
    inc_links = [{"source": "Revenue", "target": "Cost of revenue", "value": cogs},
                 {"source": "Revenue", "target": "Gross profit", "value": gross},
                 {"source": "Gross profit", "target": "Research & development", "value": rd},
                 {"source": "Gross profit", "target": "Sales, general & administrative",
                  "value": sga}]
    if other_opex:
        inc_nodes.append({"name": "Other operating", "role": "cost"})
        inc_links.append({"source": "Gross profit", "target": "Other operating",
                          "value": other_opex})
    inc_nodes.append({"name": "Operating income", "role": "stage"})
    inc_links.append({"source": "Gross profit", "target": "Operating income", "value": opinc})

    # Non-operating items are a COST when they consume operating income and a
    # SOURCE when they add to it. A company with net interest income has the
    # second shape, and forcing it into the first would draw a negative ribbon.
    if non_op >= 0:
        inc_nodes.append({"name": "Interest and other, net", "role": "cost"})
        inc_links.append({"source": "Operating income", "target": "Interest and other, net",
                          "value": non_op})
        inc_links.append({"source": "Operating income", "target": "Pre-tax income",
                          "value": pretax})
    else:
        inc_nodes.append({"name": "Interest and other, net", "role": "source"})
        inc_links.append({"source": "Operating income", "target": "Pre-tax income",
                          "value": opinc})
        inc_links.append({"source": "Interest and other, net", "target": "Pre-tax income",
                          "value": -non_op})
    inc_nodes.append({"name": "Pre-tax income", "role": "stage"})
    inc_nodes.append({"name": "Income tax", "role": "cost"})
    inc_links.append({"source": "Pre-tax income", "target": "Income tax", "value": tax})
    if nci:
        inc_nodes.append({"name": "Non-controlling interests", "role": "cost"})
        inc_links.append({"source": "Pre-tax income", "target": "Non-controlling interests",
                          "value": nci})
    inc_nodes.append({"name": "Net income", "role": "retained"})
    inc_links.append({"source": "Pre-tax income", "target": "Net income", "value": net})

    # ------------------------------------------------------------------ cash
    ocf = _m(cash["netCashProvidedByOperatingActivities"])
    capex = abs(_m(cash["investmentsInPropertyPlantAndEquipment"]))
    purchases = abs(_m(cash["purchasesOfInvestments"]))
    maturities = abs(_m(cash["salesMaturitiesOfInvestments"]))
    debt_issued = _m(cash["netDebtIssuance"])
    stock_issued = _m(cash["netStockIssuance"])
    dividends = abs(_m(cash["netDividendsPaid"]))
    other_fin = abs(_m(cash["otherFinancingActivities"]))
    cash_up = _m(cash["netChangeInCash"])

    sources = [("Operating cash flow", ocf), ("Debt issued, net", debt_issued),
               ("Stock issued, net", stock_issued), ("Investment maturities", maturities)]
    uses = [("Capital expenditure", capex), ("Investment purchases", purchases),
            ("Dividends", dividends), ("Other financing", other_fin)]
    sources = [(n, v) for n, v in sources if v > 0]
    uses = [(n, v) for n, v in uses if v > 0]

    # Currency effects plus whatever the statement does not reconcile. Named and
    # shown as its own ribbon, because a plug folded into a real line is a lie
    # about that line. ORCL FY2026: $96m forex + $96m the source does not explain.
    retained_cash = max(cash_up, 0)
    plug = (sum(v for _, v in uses) + retained_cash) - sum(v for _, v in sources)
    if plug > 0:
        sources.append(("Other and currency, net", plug))
    elif plug < 0:
        uses.append(("Other and currency, net", -plug))

    available = sum(v for _, v in sources)
    assert available == sum(v for _, v in uses) + retained_cash, (
        f"{symbol}: cash sources {available} != uses {sum(v for _, v in uses)} "
        f"+ retained {retained_cash}")

    cash_nodes = ([{"name": n, "role": "source"} for n, _ in sources]
                  + [{"name": "Cash available", "role": "stage"}]
                  + [{"name": n, "role": "cost"} for n, _ in uses]
                  + [{"name": "Increase in cash", "role": "retained"}])
    cash_links = ([{"source": n, "target": "Cash available", "value": v} for n, v in sources]
                  + [{"source": "Cash available", "target": n, "value": v} for n, v in uses]
                  + [{"source": "Cash available", "target": "Increase in cash",
                      "value": retained_cash}])

    # -------------------------------------------------------------- position
    def bs_pair(fn):
        return [fn(bs_prev), fn(bs_now)]

    cash_inv = bs_pair(lambda r: _m(r["cashAndShortTermInvestments"]) + _m(r["longTermInvestments"]))
    receiv = bs_pair(lambda r: _m(r["netReceivables"]))
    ppe = bs_pair(lambda r: _m(r["propertyPlantEquipmentNet"]))
    goodwill = bs_pair(lambda r: _m(r["goodwillAndIntangibleAssets"]))
    assets = bs_pair(lambda r: _m(r["totalAssets"]))
    payables = bs_pair(lambda r: _m(r["totalPayables"]))
    debt = bs_pair(lambda r: _m(r["totalDebt"]))
    liab = bs_pair(lambda r: _m(r["totalLiabilities"]))
    equity = bs_pair(lambda r: _m(r["totalEquity"]))
    other_assets = [assets[i] - cash_inv[i] - receiv[i] - ppe[i] - goodwill[i] for i in (0, 1)]
    other_liab = [liab[i] - payables[i] - debt[i] for i in (0, 1)]

    for i in (0, 1):
        assert liab[i] + equity[i] == assets[i], (
            f"{symbol}: assets != liabilities + equity in column {i}")

    bs_assets = [("Cash and investments", cash_inv), ("Receivables", receiv),
                 ("Property, plant and equipment", ppe),
                 ("Goodwill and intangibles", goodwill), ("Other assets", other_assets)]
    bs_claims = [("Payables", payables, "cost"), ("Debt, including leases", debt, "cost"),
                 ("Other liabilities", other_liab, "cost"), ("Equity", equity, "retained")]

    bs_rows = ([{"label": "Assets", "cells": ["", ""], "kind": "section"}]
               + [{"label": n, "cells": v, "kind": "detail"} for n, v in bs_assets]
               + [{"label": "Total assets", "cells": assets, "kind": "subtotal"},
                  {"label": "Liabilities", "cells": ["", ""], "kind": "section"}]
               + [{"label": n, "cells": v, "kind": "detail"}
                  for n, v, _ in bs_claims if n != "Equity"]
               + [{"label": "Total liabilities", "cells": liab, "kind": "subtotal"},
                  {"label": "Equity", "cells": equity, "kind": "total"}])

    bs_nodes = ([{"name": n, "role": "source"} for n, _ in bs_assets]
                + [{"name": "Total assets", "role": "stage"}]
                + [{"name": n, "role": r} for n, _, r in bs_claims])
    bs_links = ([{"source": n, "target": "Total assets", "value": v[1]} for n, v in bs_assets]
                + [{"source": "Total assets", "target": n, "value": v[1]}
                   for n, v, _ in bs_claims])

    # The picture and the table are fed from the same lists above, so they cannot
    # disagree — but assert it anyway, because "cannot" has a short half-life.
    assert sum(v[1] for _, v in bs_assets) == assets[1], f"{symbol}: sankey assets != total"
    assert sum(v[1] for _, v, _ in bs_claims) == assets[1], f"{symbol}: sankey claims != total"
    table_labels = {r["label"] for r in bs_rows}
    for name, _ in bs_assets:
        assert name in table_labels, f"{symbol}: sankey node {name!r} not in the table"

    equity_share = 100 * equity[1] / assets[1]

    # ----------------------------------------------------------- composite Z
    working_capital = _m(bs_now["totalCurrentAssets"]) - _m(bs_now["totalCurrentLiabilities"])
    retained_earnings = _m(bs_now["retainedEarnings"])
    ebit = _m(latest["ebit"])
    market_cap = _m(quote["marketCap"])
    z_inputs = [("Working capital / assets", 1.2, working_capital / assets[1]),
                ("Retained earnings / assets", 1.4, retained_earnings / assets[1]),
                ("EBIT / assets", 3.3, ebit / assets[1]),
                ("Market cap / liabilities", 0.6, market_cap / liab[1]),
                ("Revenue / assets", 1.0, rev / assets[1])]
    z_score = sum(c * v for _, c, v in z_inputs)
    z_band, z_tone = (("Distress", "bad") if z_score < 1.8
                      else ("Grey", "neutral") if z_score < 3.0 else ("Safe", "good"))

    # ------------------------------------------------------------- per share
    shares = [r["weightedAverageShsOut"] / 1e6 for r in inc]
    eps = [r["eps"] for r in inc]
    revenue_series = [_m(r["revenue"]) for r in inc]
    fcf_series = [_m(r["freeCashFlow"]) for r in cf][-len(inc):]
    n = len(inc)
    # Round the endpoints FIRST, then derive the movement as their difference.
    # Rounding opening, closing and movement independently breaks the tie
    # (round(a) + round(b-a) != round(b) in general) — which the assertion below
    # caught on AAPL, where the endpoints are ~15,000M and the movement is small.
    sh_round = [round(s) for s in shares]
    roll_rows = [
        {"label": "Opening", "cells": sh_round[:-1], "kind": "opening"},
        {"label": "Net shares issued",
         "cells": [sh_round[i + 1] - sh_round[i] for i in range(n - 1)], "kind": "movement"},
        {"label": "Closing", "cells": sh_round[1:], "kind": "closing"},
    ]
    for i in range(n - 1):
        assert (roll_rows[0]["cells"][i] + roll_rows[1]["cells"][i]
                == roll_rows[2]["cells"][i]), f"{symbol}: share roll-forward does not tie"

    rps = [r / s for r, s in zip(revenue_series, shares)]
    fps = [f / s for f, s in zip(fcf_series, shares)]
    pershare_rows = [
        {"label": "Revenue per share", "cells": [round(v, 2) for v in rps],
         "cagr": _cagr(rps[0], rps[-1], n - 1), "dir": _arrow(_cagr(rps[0], rps[-1], n - 1))},
        {"label": "Earnings per share", "cells": eps,
         "cagr": _cagr(eps[0], eps[-1], n - 1), "dir": _arrow(_cagr(eps[0], eps[-1], n - 1))},
        {"label": "Free cash flow per share", "cells": [round(v, 2) for v in fps],
         "cagr": _cagr(fps[0], fps[-1], n - 1), "dir": _arrow(_cagr(fps[0], fps[-1], n - 1))},
    ]

    # -------------------------------------------------------------- segments
    seg_raw = sorted(p["revenue-product-segmentation"], key=lambda r: r["fiscalYear"])[-5:]
    seg_years = [f"FY{r['fiscalYear']}" for r in seg_raw]
    seg_names = sorted({k for r in seg_raw for k in r["data"]},
                       key=lambda k: -seg_raw[-1]["data"].get(k, 0))
    # `points`, not `values` — a chart series feeds stacked_area/stacked_normalized,
    # and `values` is a dict method Jinja would resolve before the key.
    seg_series = [{"name": _seg_label(k), "points": [_m(r["data"].get(k, 0)) for r in seg_raw]}
                  for k in seg_names]
    seg_totals = [sum(s["points"][i] for s in seg_series) for i in range(len(seg_raw))]
    segment_lag = seg_years[-1] != years[-1]

    # NO PROFIT KEYS. `revenue-product-segmentation` publishes revenue only, and
    # the component now omits the profit columns rather than being handed
    # revenue twice — which would have rendered a margin of 100% for every
    # segment and looked entirely plausible.
    seg_rows = []
    for s in seg_series:
        last = s["points"][-1]
        seg_rows.append({
            "segment": s["name"], "revenue": last,
            "rev_share": 100 * last / seg_totals[-1],
            "growth": 100 * (last / s["points"][-2] - 1) if s["points"][-2] else 0,
        })
    seg_total_row = {"label": "Total",
                     "cells": [f"{seg_totals[-1]:,}", "100.0%",
                               f"{100 * (seg_totals[-1] / seg_totals[-2] - 1):.1f}%"]}

    seg_trend_rows = [
        {"label": s["name"], "cells": s["points"],
         "cagr": _cagr(s["points"][0], s["points"][-1], len(seg_raw) - 1),
         "dir": _arrow(_cagr(s["points"][0], s["points"][-1], len(seg_raw) - 1))}
        for s in seg_series
    ] + [{"label": "Total revenue", "cells": seg_totals,
          "cagr": _cagr(seg_totals[0], seg_totals[-1], len(seg_raw) - 1),
          "dir": _arrow(_cagr(seg_totals[0], seg_totals[-1], len(seg_raw) - 1))}]

    deltas = sorted(((s["name"], s["points"][-1] - s["points"][0]) for s in seg_series),
                    key=lambda kv: -kv[1])
    bridge_steps = ([{"label": f"{seg_years[0]} revenue", "delta": seg_totals[0], "kind": "start"}]
                    + [{"label": nm, "delta": dv, "kind": "up" if dv >= 0 else "down"}
                       for nm, dv in deltas]
                    + [{"label": f"{seg_years[-1]} revenue", "delta": seg_totals[-1],
                        "kind": "end"}])
    assert seg_totals[0] + sum(d for _, d in deltas) == seg_totals[-1], (
        f"{symbol}: bridge steps do not carry {seg_totals[0]} to {seg_totals[-1]}")

    # --------------------------------------------------------------- margins
    def ratio(values):
        return [100 * v / r for v, r in zip(values, revenue_series)]

    gm = ratio([_m(r["grossProfit"]) for r in inc])
    om = ratio([_m(r["operatingIncome"]) for r in inc])
    roic = [100 * (r.get("returnOnInvestedCapital") or 0) for r in km]
    margin_rows = []
    for label, vals in [("Gross margin", gm),
                        ("R&D / revenue", ratio([_m(r["researchAndDevelopmentExpenses"]) for r in inc])),
                        ("Operating margin", om),
                        ("Net margin", ratio([_m(r["netIncome"]) for r in inc])),
                        ("Return on invested capital", roic)]:
        delta = vals[-1] - vals[0]
        margin_rows.append({"label": label, "cells": [round(v, 1) for v in vals],
                            "cagr": delta * 100, "cagr_fmt": "bps", "dir": _arrow(delta)})

    # ----------------------------------------------------------------- peers
    peer_headers = ["ROIC", "Capex / revenue", "R&D / revenue", "SBC / revenue", "EV/EBITDA"]
    peer_formats = ["pct", "pct", "pct", "pct", "num"]

    def peer_cells(metrics):
        return [100 * (metrics.get("returnOnInvestedCapital") or 0),
                100 * (metrics.get("capexToRevenue") or 0),
                100 * (metrics.get("researchAndDevelopementToRevenue") or 0),
                100 * (metrics.get("stockBasedCompensationToRevenue") or 0),
                metrics.get("evToEBITDA") or 0]

    peer_rows = [{"name": profile.get("companyName", symbol), "cells": peer_cells(km_now),
                  "subject": True}]
    for ticker, metrics in (p.get("_peers") or {}).items():
        peer_rows.append({"name": ticker, "cells": peer_cells(metrics[0]), "subject": False})
    # `headers` is the METRIC columns only — the macro emits Company itself.
    for row in peer_rows:
        assert len(row["cells"]) == len(peer_headers), (
            f"{symbol}: peer row {row['name']!r} has {len(row['cells'])} cells "
            f"for {len(peer_headers)} headers")

    # ------------------------------------------------- sankey label hygiene
    # Sankey labels are drawn as CANVAS TEXT and never pass an HTML parser, so
    # "&amp;" would render as five literal characters.
    for group in (inc_nodes, cash_nodes, bs_nodes):
        for node in group:
            assert "&" not in node["name"] or "&amp;" not in node["name"], \
                f"{symbol}: HTML entity in sankey label {node['name']!r}"
            assert "&rsquo;" not in node["name"] and "&nbsp;" not in node["name"], \
                f"{symbol}: HTML entity in sankey label {node['name']!r}"

    # --------------------------------------------------------------- assemble
    unit = "$ millions"
    d = {
        "slug": symbol.lower(),
        "title": f"{profile.get('companyName', symbol)} — Financial Profile",
        "ticker": symbol,
        "company": profile.get("companyName", symbol),
        "exchange": profile.get("exchange", ""),
        "sector": profile.get("sector", ""),
        "unit": unit,
        "period": years[-1],
        "period_end": period_end.strftime("%d %B %Y"),
        "filed": filed.strftime("%d %B %Y"),
        "report_date": report_date.strftime("%d %B %Y"),
        "staleness_days": (report_date - period_end).days,
        "price": quote["price"],
        "price_date": report_date.strftime("%d %B %Y"),
        "market_cap": market_cap,
        "header_facts": [
            {"label": "Price", "value": f"${quote['price']:,.2f}"},
            {"label": "Market cap", "value": f"${market_cap / 1000:,.0f}B"},
            {"label": f"Revenue {years[-1]}", "value": f"${rev / 1000:,.1f}B"},
            {"label": f"Net income {years[-1]}", "value": f"${net / 1000:,.1f}B"},
            {"label": "Sector", "value": profile.get("sector", "—")},
        ],
        "basis_facts": [
            {"term": "Report date",
             "value": f"{report_date:%d %B %Y} — every date below is measured against it"},
            {"term": "Latest period",
             "value": f"{years[-1]}, ended {period_end:%d %B %Y} — "
                      f"{(report_date - period_end).days} days before this report"},
            {"term": "Filed", "value": f"{filed:%d %B %Y}"},
            {"term": "Price as of",
             "value": f"{report_date:%d %B %Y}. A market price is not a filing date; "
                      f"market-cap-sensitive figures below carry this one"},
            {"term": "Currency and unit",
             "value": f"{latest.get('reportedCurrency', 'USD')}, {unit} unless stated"},
            {"term": "Segment exhibits",
             "value": (f"{seg_years[0]}–{seg_years[-1]}: product-line revenue is published "
                       f"only through {seg_years[-1]} in this feed, so those exhibits run "
                       f"behind the rest" if segment_lag
                       else f"{seg_years[0]}–{seg_years[-1]}, aligned with the statements")},
            {"term": "Derived figures",
             "value": (f"free cash flow per share and the Altman Z are computed here"
                       + (f"; the ${other_opex:,}m 'other operating' line absorbs an "
                          f"inconsistency in the source between operating income and the "
                          f"expense lines" if other_opex else "")
                       + (f"; the ${abs(plug):,}m 'other and currency' cash line absorbs "
                          f"currency effects and what the statement does not reconcile"
                          if plug else ""))},
            {"term": "Source",
             "value": "company filings via Financial Modeling Prep; derived figures marked"},
        ],
        # income
        "inc_nodes": inc_nodes, "inc_links": inc_links,
        "inc_caption": f"{profile.get('companyName', symbol)} {years[-1]} — revenue to net income",
        "seg_rows": seg_rows,
        "seg_total_row": seg_total_row,
        "seg_caption": f"Revenue by segment, {seg_years[-1]}",
        "seg_years": seg_years,
        # cash
        "cash_nodes": cash_nodes, "cash_links": cash_links,
        "cash_caption": f"{profile.get('companyName', symbol)} {years[-1]} — cash generated and deployed",
        # position
        "bs_nodes": bs_nodes, "bs_links": bs_links,
        "bs_periods": [_fy(bs_prev), _fy(bs_now)],
        "bs_rows": bs_rows,
        "bs_caption": f"Balance sheet — {_fy(bs_now)} against {_fy(bs_prev)}",
        "bs_sankey_caption": f"{profile.get('companyName', symbol)} — what it owns and who has a claim on it",
        "bs_check": f"{assets[1]:,} = {liab[1]:,} + {equity[1]:,}",
        "bs_unit": f"{unit}, at {period_end:%d %B %Y}",
        "equity_share": equity_share,
        "z_name": "Altman Z",
        "z_formula": "Z = 1.2·WC/A + 1.4·RE/A + 3.3·EBIT/A + 0.6·MC/L + 1.0·S/A",
        "z_inputs": [{"component": c, "coefficient": k, "value": v, "contribution": k * v}
                     for c, k, v in z_inputs],
        "z_score": round(z_score, 2), "z_band": z_band, "z_tone": z_tone,
        "z_bands": [{"label": "Distress", "range": "< 1.8", "tone": "bad"},
                    {"label": "Grey", "range": "1.8–3.0", "tone": "neutral"},
                    {"label": "Safe", "range": "> 3.0", "tone": "good"}],
        "piotroski": scores.get("piotroskiScore"),
        # per share
        "share_periods": years[1:],
        "roll_rows": roll_rows,
        "pershare_rows": pershare_rows,
        "periods": years,
        # evolution
        "seg_trend_rows": seg_trend_rows,
        "seg_series": seg_series,
        "seg_totals": seg_totals,
        "bridge_steps": bridge_steps,
        "bridge_min": 0,
        "bridge_max": int(seg_totals[-1] * 1.05),
        "bridge_caption": f"Revenue bridge, {seg_years[0]} to {seg_years[-1]} ({unit})",
        "margin_rows": margin_rows,
        # peers
        "peer_headers": peer_headers, "peer_formats": peer_formats, "peer_rows": peer_rows,
        "peer_caption": "Peers — fiscal years ending on different dates",
    }
    d.update(PROSE)
    return d
