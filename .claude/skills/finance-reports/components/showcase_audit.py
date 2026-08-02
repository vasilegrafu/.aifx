"""Generate the audit page — every showcase checked in one browser load.

    python components/showcase_audit.py        ->  Path to showcase_audit.html

Then serve the repo and open it. The page walks every showcase in an iframe
and reports what a build cannot see.

WHY THIS EXISTS. `showcase_builder.py --check` proves a page is CURRENT; it
cannot prove the page is RIGHT. Three defects have shipped past a clean build
so far, and every one of them rendered as valid markup with valid JSON:

    valuation-range   bars ran past their track, because scale_min/scale_max
                      default to 0..100 and the data was in dollars
    gauge             "78.4percent", because a unit word reached a slot that
                      wanted a symbol
    stacked-h-bar     axis labels clipped, because the grid reserved too little

All three are LAYOUT facts. They exist only once a browser has applied the CSS,
which is why they survived the builder, the validators, and me reading the
markup. The audit runs the checks that need a rendered box.

It is a REVIEW PROMPT, NOT A GATE. A flag means look; some are fine. It cannot
see a chart that is simply wrong, only one that has left its box.
"""

import argparse
import io
import json
import sys
from pathlib import Path

COMPONENTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = COMPONENTS_DIR.parent

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from components._showcase_controller import PAGE          # noqa: E402
from components.showcase_builder import ShowcaseBuilder   # noqa: E402

AUDIT_PAGE = "showcase_audit.html"

#: Letter runs that legitimately touch a digit, so the glued-text check does
#: not report every "100bps". Compared lowercased against the run alone.
ALLOWED_RUNS = ["bps", "pts", "pt", "bn", "mn", "tn", "kg", "km", "sqft",
                "yoy", "qoq", "mom", "cagr", "year", "yr", "day", "hr"]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>showcase audit</title>
<style>
  body {{ font: 14px/1.5 system-ui, sans-serif; margin: 2rem; }}
  h1 {{ font-size: 1.3rem; }}
  #probe {{ width: 1100px; height: 2400px; border: 0;
            position: absolute; left: -20000px; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ text-align: left; padding: .35rem .6rem;
            border-bottom: 1px solid #ddd; vertical-align: top; }}
  th {{ background: #f4f4f4; }}
  td.kind {{ white-space: nowrap; font-family: ui-monospace, monospace; }}
  td.detail {{ font-family: ui-monospace, monospace; font-size: 12px;
               word-break: break-word; }}
  .ok {{ color: #0a7c2f; }}
  .bad {{ color: #b00020; }}
  #summary {{ font-size: 1.05rem; margin-top: 1rem; }}
</style>
</head>
<body>
<h1>showcase audit</h1>
<p id="summary">running…</p>
<table id="out"><thead><tr>
  <th>component</th><th>check</th><th>detail</th>
</tr></thead><tbody></tbody></table>
<iframe id="probe"></iframe>
<script>
const PAGES = {pages};
const ALLOWED = {allowed};
const PAGE = {page};
const SETTLE_MS = 700;   // charts draw after load; canvas needs a beat

// ---------------------------------------------------------------- the checks

// Every check answers the same question: is something outside the box that was
// drawn for it? That is the class of defect a build cannot see.
function checks(doc, win) {{
  const out = [];
  const de = doc.documentElement;

  // Guard first. If the stylesheet did not arrive, nothing below means
  // anything -- an unstyled page overflows everywhere and would bury the
  // real findings under noise.
  const styled = win.getComputedStyle(doc.body).maxWidth !== 'none'
              || doc.styleSheets.length > 0;
  if (!styled) {{
    out.push(['assets-missing', 'no stylesheet applied; other checks skipped']);
    return out;
  }}

  // 1. The page itself scrolls sideways. This is what valuation-range did.
  if (de.scrollWidth > de.clientWidth + 1) {{
    out.push(['page-overflow',
      `scrollWidth ${{de.scrollWidth}} > clientWidth ${{de.clientWidth}}`]);
  }}

  // 2. A percentage driving a width is outside 0..100. The library sets bar
  // geometry through data-* attributes, so this reads the actual instruction
  // rather than the result -- it fires even when the overflow is clipped
  // away and never reaches check 1.
  for (const el of doc.querySelectorAll('*')) {{
    for (const attr of el.attributes) {{
      if (!attr.name.startsWith('data-')) continue;
      const m = /^(-?[\\d.]+)%$/.exec(attr.value.trim());
      if (!m) continue;
      const n = parseFloat(m[1]);
      if (n < 0 || n > 100) {{
        out.push(['pct-out-of-track',
          `<${{el.tagName.toLowerCase()}} class="${{el.className}}"> `
          + `${{attr.name}}="${{attr.value}}"`]);
      }}
    }}
  }}

  // 3. Text clipped by its own container.
  for (const el of doc.querySelectorAll('*')) {{
    if (el.children.length || !el.textContent.trim()) continue;
    const cs = win.getComputedStyle(el);
    if (cs.overflowX === 'visible') continue;
    if (el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1) {{
      out.push(['clipped',
        `<${{el.tagName.toLowerCase()}} class="${{el.className}}"> `
        + `"${{el.textContent.trim().slice(0, 40)}}"`]);
    }}
  }}

  // 4. A word run welded to a number -- "USD per share0", "78.4percent".
  // Both directions, because the unit can land on either side, and a run of
  // three lets "Q1" and "FY25" through without an allowlist entry each.
  const walk = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
  for (let node; (node = walk.nextNode()); ) {{
    const tag = node.parentElement && node.parentElement.tagName;
    if (tag === 'SCRIPT' || tag === 'STYLE') continue;
    const text = node.nodeValue;
    for (const hit of text.matchAll(/[a-z]{{3,}}\\d|\\d[a-z]{{3,}}/g)) {{
      const run = hit[0].replace(/[\\d.]/g, '').toLowerCase();
      if (ALLOWED.includes(run)) continue;
      out.push(['glued-text', `"${{hit[0]}}" in "${{text.trim().slice(0, 60)}}"`]);
    }}
  }}
  return out;
}}

// ----------------------------------------------------------------- the walk

const frame = document.getElementById('probe');
const body = document.querySelector('#out tbody');
const results = [];

function row(component, kind, detail) {{
  const tr = body.insertRow();
  tr.insertCell().textContent = component;
  const k = tr.insertCell(); k.textContent = kind; k.className = 'kind';
  const d = tr.insertCell(); d.textContent = detail; d.className = 'detail';
}}

function load(url) {{
  return new Promise(resolve => {{
    frame.onload = () => setTimeout(resolve, SETTLE_MS);
    frame.src = url;
  }});
}}

(async () => {{
  for (const component of PAGES) {{
    const url = component + '/' + PAGE;
    let found;
    try {{
      await load(url);
      found = checks(frame.contentDocument, frame.contentWindow);
    }} catch (e) {{
      found = [['unreadable', String(e)]];
    }}
    for (const [kind, detail] of found) {{
      results.push({{component, kind, detail}});
      row(component, kind, detail);
    }}
  }}
  const summary = document.getElementById('summary');
  const n = new Set(results.map(r => r.component)).size;
  summary.textContent =
    `${{PAGES.length}} showcase(s) checked, ${{results.length}} `
    + `flag(s) across ${{n}} component(s)`;
  summary.className = results.length ? 'bad' : 'ok';
  // The result any caller reads -- a browser tool evaluates this, so the
  // findings do not have to be scraped back out of the table.
  window.__AUDIT__ = {{done: true, checked: PAGES.length, results}};
}})();
</script>
</body>
</html>
"""


def build() -> Path:
    """Write the audit page listing every showcase that currently exists.

    Generated rather than edited, for the same reason the showcases are: the
    list of components is a fact about the tree, and a hand-kept copy of it
    goes stale the first time somebody adds a component and does not know
    this file exists."""
    pages = ShowcaseBuilder().all()
    page = COMPONENTS_DIR / AUDIT_PAGE
    io.open(page, "w", encoding="utf-8", newline="\n").write(
        TEMPLATE.format(pages=json.dumps(pages, indent=0),
                        allowed=json.dumps(ALLOWED_RUNS),
                        page=json.dumps(PAGE)))
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="showcase_audit.py",
        description="generate the page that checks every showcase in a browser")
    parser.parse_args(argv)
    page = build()
    print(page)
    print(f"{len(ShowcaseBuilder().all())} showcase(s) listed")
    # Plain hyphens: stdout is cp1252 on Windows.
    print("serve the repo root, then open "
          ".claude/skills/finance-reports/components/" + AUDIT_PAGE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
