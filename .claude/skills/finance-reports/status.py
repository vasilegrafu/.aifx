"""What is in this tree, and does it hang together. Exit 0 or 1.

    python .claude/skills/finance-reports/status.py           # the details
    python .claude/skills/finance-reports/status.py --check   # exit 1 if anything is stale

WHY THIS EXISTS -- TWO REASONS, and they are the same reason twice.

(1) A COUNT IN PROSE IS A CLAIM ABOUT THE TREE AT THE MOMENT SOMEBODY TYPED IT.
"61 of the components carry a hyphen", "23 components namespaced fa-", "25
macros across 15 components" -- every one of those was true when it was written
and none of them can announce that it stopped being. `CATALOG.md` states its
count and cannot be wrong, because it is generated; a sentence in a REFERENCE
has no such protection. So the counts came out of the prose and landed here,
where they are read off the tree on demand and are therefore never stale. The
rule this leaves behind: a number that describes the tree NOW belongs in this
script, and a number that argues something happened at a moment ("62 of 110
files had no `## Rules` when the audit was written") stays in prose and says so.

(2) FINISHING A COMPONENT OR A REPORT MEANT REMEMBERING FOUR COMMANDS. Both
catalogues, every showcase page, the usage.md skeleton -- four exit codes and no
single thing to type at the end of a procedure. Four commands remembered
separately are four commands run separately, which in practice means the last
one is not run at all. `--check` is one command for the end of `SKILL.md`'s
"Adding a component" and "Adding a report".

WHAT IT CHECKS -- six things, of two kinds, and the difference decides how each
one is run:

  THREE HAVE AN ENGINE. Both catalogues and every showcase page are checked by
  the builder that generates them, so those are run as commands and their exit
  codes are reported. Each engine owns its own definition of stale and already
  expresses it that way; importing them would make this file a second opinion
  about what "out of date" means, and two of the three raise SystemExit rather
  than returning a status, so it would also mean catching control flow to
  re-derive an answer a subprocess hands over for free. What this prints is
  then literally what typing the command yourself would have printed.

  TWO HAVE NO ENGINE, so they are computed here, because here is the only place
  they could live. `nonconforming()` checks every usage.md against the skeleton
  in SKILL.md -- it absorbed usage_audit.py, which was one file for one check
  and is gone. `unbundled()` checks that `css/bundle.css` @imports every
  stylesheet under `css/` and `js/bundle.js` lists every module under
  `js/modules/`; both bundles are hand-maintained entry files by design
  ("adding a feature: create js/modules/<name>.js, then add <name> here"), so a
  file can be written, styled and committed while being loaded by nothing. It
  renders as a component with no CSS, which looks like a styling bug and is a
  missing line in a manifest.

That split is the rule to keep if a sixth check arrives: a check an engine can
own belongs to that engine and is run from here, and only a check with no
possible owner is written here.

WHY IT SITS AT THE SKILL ROOT: "there is no top-level dispatcher" is a real rule
here and this does not break it. A dispatcher ROUTES work to the engine that
owns it -- it takes a target and picks a builder. This takes no target, builds
nothing, writes nothing; it reads the tree and reports. It is at the root
because it spans both sides, and a per-side copy would be two answers to "what
is in here".

The discovery rule is the one everything else here uses: a directory holding
`component.html.j2` IS a component, a directory holding `report.html.j2` IS a
report. Nothing is registered, so a new item appears in this output the day it
appears in the tree, without this file being told.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from _paths import CDN_SUFFIX, VERSION_FILE                          # noqa: E402

#: How to invoke this from the PROJECT ROOT, where a session starts. Derived
#: from where the skill actually sits, so a copy under another name still
#: prints a command that runs.
COMMAND = f"python {CDN_SUFFIX}/status.py"

MARKUP = "component.html.j2"
REPORT_VIEW = "report.html.j2"
CONTROLLER = "showcase_controller.py"
SHOWCASE_VIEW = "showcase.html.j2"

#: The checks another file already owns, in the order a procedure runs them:
#: the two indexes, then the pages. Each is (label, argv-tail); the interpreter
#: running THIS script runs them, so a venv cannot be lost between one command
#: and the next.
CHECKS = (
    ("components/CATALOG.md", ["components/catalog_builder.py", "--check"]),
    ("reports/CATALOG.md", ["reports/catalog_builder.py", "--check"]),
    ("showcase pages", ["components/showcase_builder.py", "--all", "--check"]),
)

IMPORTED = re.compile(r"""@import\s+url\(["']([^"']+)["']\)""")
MODULES = re.compile(r"var\s+MODULES\s*=\s*\[(.*?)\]", re.S)

USAGE = "usage.md"
RULES = "## Rules"

#: Which prefix each directory owns. The KEY is the folder a component lives
#: in, the value the prefix its classes must carry -- the house rule in
#: SKILL.md, as data. `foundational` is deliberately absent: its classes are
#: unprefixed, so it owns no prefix and may use none of these.
#: Top-level component directory -> the class prefix its members carry. Every
#: chart engine's kinds wear `chart-` and every diagram engine's `diagram-`,
#: because the prefix names the SUBSYSTEM a class belongs to, not the engine
#: that happens to render it: a `.chart-note` reads the same under ECharts as
#: under Plotly, and duplicating it per engine would be three names for one rule.
OWNS = {"fundamental-analysis": "fa", "portfolio": "portfolio", "macro": "macro",
        "charts-apache-echarts": "chart", "charts-plotly": "chart",
        "charts-bokeh": "chart", "diagrams-mermaid": "diagram", "math": "math"}

#: Classes any component may carry whatever directory it lives in, because they
#: are not directory names at all. `katex`, `mermaid` and `apache-echarts` are
#: ENGINE markup hooks a published document carries -- bundle.css names those
#: three as the exceptions -- and `math`, `chart` and `diagram` bare are the
#: rendering subsystems, which every tier is allowed to draw on.
HOOKS = {"katex", "mermaid", "apache-echarts", "math", "chart", "diagram"}

CLASS_ATTR = re.compile(r'class="([^"{}]*)"')
#: Every class attribute, INCLUDING the ones carrying Jinja -- `unstyled()` has
#: to see those to learn which prefixes are built dynamically.
CLASS_ATTR_ANY = re.compile(r'class="([^"]*)"')


# --------------------------------------------------------------------- read
def components() -> list[Path]:
    """Every component directory, sorted. The marker IS the definition."""
    return sorted(m.parent for m in (SKILL_DIR / "components").rglob(MARKUP))


def reports() -> list[Path]:
    """Every report directory, sorted."""
    return sorted(v.parent for v in (SKILL_DIR / "reports").rglob(REPORT_VIEW))


def version() -> dict:
    """version.json, or an empty dict if this project has none.

    Not an error here even though it is one for every builder: this script is
    the thing you run to find out what is wrong, so it has to survive the
    project it is describing being incomplete. A copied skill with no
    version.json cannot render a single page, and saying so plainly is more
    use than a traceback."""
    try:
        return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def nonconforming() -> list[str]:
    """Every usage.md that does not follow the skeleton, and why.

    THREE ASSERTIONS, and deliberately no more than SKILL.md actually mandates:
    the file exists, it opens with an H1, it carries `## Rules`. SKILL.md says
    the heading names "may vary where the item genuinely differs -- a report has
    no markup and a component has no fetch", so `## Markup` and `## Build it`
    are NOT asserted; only `## Rules`, which the same paragraph calls not
    optional. Checking the soft ones would fail files that are right, and a
    check that cries wolf earns an ignore rule rather than a fix.

    Nor is the H1 required to equal the folder name. Two files deliberately
    differ (`apache-echarts` titles itself `chart-apache-echarts`), naming the
    reader's term rather than the directory's. What matters is that the file
    opens by saying what it is.

    WHY THIS IS ENFORCED AT ALL, since it is the one check here with no engine
    behind it: it is the convention that drifted. When it was first measured, 62
    of 110 usage.md carried no `## Rules` heading -- while SKILL.md called it not
    optional, and every other convention in this skill had an exit code. That is
    not a fact about those 62 authors; it is what an unenforced convention
    converges to. A rule with no exit code is a preference.

    A usage.md is also the ONLY per-item documentation that exists. The
    catalogues render "**no usage.md**" for a component that has none, but that
    is display: it is catalogued as choosable and undocumented, and the build
    stays green. This is the thing that does not.
    """
    reasons = []
    for kind, directory in (
            [("component", d.parent) for d in
             sorted((SKILL_DIR / "components").rglob(MARKUP))] +
            [("report", d.parent) for d in
             sorted((SKILL_DIR / "reports").rglob(REPORT_VIEW))]):
        where = f"{directory.relative_to(SKILL_DIR).as_posix()}  ({kind})"
        usage = directory / USAGE
        if not usage.exists():
            reasons.append(f"{where}: no {USAGE} at all - every component and "
                           f"every report has one")
            continue

        text = usage.read_text(encoding="utf-8")
        first = next((line for line in text.splitlines() if line.strip()), "")
        if not first.startswith("# "):
            reasons.append(f"{where}: does not open with an H1 naming what this is")
        if RULES not in text:
            # The content is usually already written; it is a heading that is
            # missing, not a section. Saying which turns a rewrite into an edit.
            extra = (" - the content is already there under a prose 'Rules:'"
                     " lead-in, so this is a heading, not a rewrite"
                     if "Rules:" in text else "")
            reasons.append(f"{where}: no `{RULES}` heading{extra}")
    return reasons


def misprefixed() -> list[str]:
    """Classes used by a component that does not own their prefix.

    THE HOUSE RULE, AS AN EXIT CODE: a class is unprefixed only in
    `foundational/`; anywhere else it carries the name of the directory it lives
    in. Until 11.0.0 nothing checked that, and six classes had drifted across
    the boundary -- in both directions. Three foundational components were
    styled by `fundamental-analysis.css`, and `fa/unit-economics` was reaching
    into `portfolio.css`.

    WHY IT IS WORTH AN EXIT CODE rather than a convention. The `domain` layer
    sits AFTER `content` and `blocks`, so a foundational component borrowing a
    domain class cannot restyle its own caption -- layer order beats
    specificity, and the fix would be to edit a discipline's stylesheet. The
    reverse hurts more: anyone restyling a discipline's class silently restyles
    every foundational component that borrowed it, with nothing to warn them.

    And it is not only tidiness. `portfolio-rm-note` was SCOPED to
    `table.portfolio-riskmetrics`, so when `fa/unit-economics` asked for it the
    rule matched nothing at all: a prose column fell through to
    `table.fin td` and rendered right-aligned in tabular figures. A build
    cannot see that, validation cannot see that, and it shipped. This check is
    the thing that sees it -- not the wrong rendering, but the borrow that
    caused it.

    The fix is never to add an exception. A class two disciplines want is
    telling you it is foundational, which is what SKILL.md already says and
    what 6.0.0 and 11.0.0 both did about it.
    """
    found = []
    for markup in sorted((SKILL_DIR / "components").rglob(MARKUP)):
        parts = markup.relative_to(SKILL_DIR / "components").parts
        owner = OWNS.get(parts[1]) if parts[0] == "domain-specific" \
            else OWNS.get(parts[0])
        where = "/".join(parts[:-1])
        for attribute in CLASS_ATTR.findall(markup.read_text(encoding="utf-8")):
            for cls in attribute.split():
                if cls in HOOKS:
                    continue
                prefix = cls.split("-")[0]
                if prefix in OWNS.values() and prefix != owner:
                    owns = "owns no prefix - foundational classes are unprefixed" \
                        if owner is None else f"owns '{owner}-'"
                    found.append(f"{where} ({owns}) uses .{cls}")
                # A doubled prefix is a rename artifact, not a namespace: it
                # passes the check above, since `macro-macro-x` starts `macro`.
                if owner and cls.startswith(f"{owner}-{owner}-"):
                    found.append(f"{where} uses .{cls} - doubled '{owner}-' prefix")
    return sorted(set(found))


def unstyled() -> list[str]:
    """Classes in markup that no stylesheet and no module can reach.

    A class that styles nothing is not harmless. It reads as a styling hook to
    the next person, who either preserves it through a refactor for no reason
    or, worse, restyles the component by adding a rule for it somewhere it does
    not belong. Twelve of these had accumulated by 11.0.0 -- eight of them the
    UNPREFIXED table identity classes that also broke the namespace rule, which
    is how a dead class and a wrong class turned out to be the same finding.

    Nothing here can be reached by author CSS either: SKILL.md forbids `style=`
    and `<style>` in generated documents, so a document that leaves this tree
    carries no way to target one. A class with no rule has no possible consumer.

    THREE EXCLUSIONS, and each is why this check could not be written naively:

      1. A DYNAMIC SIBLING. `class="fa-reco-{{ tone }}"` means `.fa-reco-good`
         exists in CSS while no literal `fa-reco-good` appears in markup. Any
         class under a prefix the markup builds dynamically is therefore off
         limits to this check.
      2. JINJA CONTROL FLOW. `class="a{% if x %} b{% endif %}"` yields the
         tokens `if` and `endif` unless the block syntax is stripped as well as
         the expression syntax. Those are not classes and never were.
      3. THE ENGINES. `apache-echarts`, `mermaid` and `katex` are markup hooks a
         published document carries for a renderer, and the chart and diagram
         modules add their own classes at view time. Anything a module names in
         a string literal is reachable even with no CSS rule of its own.

    Without all three this reports a dozen false positives, and a check that
    cries wolf earns an ignore rule rather than a fix.
    """
    literal: dict[str, set[str]] = {}
    dynamic: set[str] = set()
    for view in sorted(list((SKILL_DIR / "components").rglob("*.j2"))
                       + list((SKILL_DIR / "reports").rglob("*.j2"))):
        if view.name.startswith("_"):
            continue
        text = view.read_text(encoding="utf-8")
        for attribute in CLASS_ATTR_ANY.findall(text):
            for stem in re.findall(r"([a-z][a-z0-9-]*)-?\{[{%]", attribute):
                dynamic.add(stem.rstrip("-"))
            # BOTH Jinja syntaxes, or exclusion (2) above fires on every {% if %}
            bare = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", " ", attribute)
            for cls in bare.split():
                if re.fullmatch(r"[a-z][a-z0-9-]*", cls):
                    literal.setdefault(cls, set()).add(view.parent.name)

    sheets = re.sub(r"/\*.*?\*/", " ",
                    "".join(f.read_text(encoding="utf-8")
                            for f in (SKILL_DIR / "css").rglob("*.css")), flags=re.S)
    styled = {c for block in re.findall(r"([^{}]+)\{", sheets)
              for c in re.findall(r"\.([a-z][a-z0-9-]*)", block)}
    modules = "".join(f.read_text(encoding="utf-8")
                      for f in (SKILL_DIR / "js").rglob("*.js"))

    dead = []
    for cls, users in sorted(literal.items()):
        if cls in styled or cls in HOOKS:
            continue
        if any(cls == stem or cls.startswith(stem + "-") for stem in dynamic):
            continue
        if re.search(rf"['\"`][^'\"`]*\b{re.escape(cls)}\b", modules):
            continue
        dead.append(f".{cls} styles nothing - used by {', '.join(sorted(users))}")
    return dead


def unbundled() -> list[str]:
    """Stylesheets and JS modules that exist but nothing loads.

    Both bundles are hand-maintained manifests -- that is deliberate, and it is
    also the failure: a file written, styled and committed while being loaded
    by nothing renders as a component with no CSS, which reads as a styling bug
    rather than as a missing line in a list."""
    orphans = []

    css_dir = SKILL_DIR / "css"
    bundle = css_dir / "bundle.css"
    if bundle.exists():
        imported = {(css_dir / href).resolve()
                    for href in IMPORTED.findall(bundle.read_text(encoding="utf-8"))}
        orphans += [f"css/{sheet.relative_to(css_dir).as_posix()}"
                    for sheet in sorted(css_dir.rglob("*.css"))
                    if sheet != bundle and sheet.resolve() not in imported]

    modules_dir = SKILL_DIR / "js" / "modules"
    entry = SKILL_DIR / "js" / "bundle.js"
    if entry.exists() and modules_dir.is_dir():
        match = MODULES.search(entry.read_text(encoding="utf-8"))
        listed = set(re.findall(r'"([^"]+)"', match.group(1))) if match else set()
        orphans += [f"js/modules/{module.name}"
                    for module in sorted(modules_dir.glob("*.js"))
                    if module.stem not in listed]

    return orphans


# -------------------------------------------------------------------- report
def inventory() -> list[str]:
    """The details: what is in the tree, counted where it is, not in prose."""
    found = components()
    by_category: dict[str, list[Path]] = {}
    for directory in found:
        relative = directory.relative_to(SKILL_DIR / "components")
        # Two levels where there are two -- `domain-specific/portfolio` is the
        # unit a namespace belongs to (`portfolio-`), and rolling it up to
        # `domain-specific` would hide the three disciplines behind one number.
        key = "/".join(relative.parts[:2]) if relative.parts[0] == "domain-specific" \
            else relative.parts[0]
        by_category.setdefault(key, []).append(directory)

    lines = [f"components  {len(found)}"]
    for category in sorted(by_category):
        members = by_category[category]
        showcased = sum(1 for d in members
                        if (d / CONTROLLER).exists() and (d / SHOWCASE_VIEW).exists())
        shown = "" if showcased == len(members) else f"   {showcased} showcased"
        lines.append(f"  {category:<38}{len(members):>4}{shown}")

    # A missing usage.md is NOT counted here, though it would be one line: the
    # skeleton check below FAILS on it and names the file, so counting it here
    # too would say one thing twice in one run. A missing SHOWCASE is counted,
    # because nothing fails on it -- it is nominally optional, so this is the
    # only place it is ever said.
    hyphenated = sum(1 for d in found if "-" in d.name)
    no_showcase = [d for d in found
                   if not ((d / CONTROLLER).exists() and (d / SHOWCASE_VIEW).exists())]
    lines += [
        "",
        f"  {'hyphenated folder names':<38}{hyphenated:>4}   "
        f"(why controllers are path-loaded, never imported)",
        f"  {'without a showcase':<38}{len(no_showcase):>4}",
    ]
    lines += [f"      {d.relative_to(SKILL_DIR).as_posix()}" for d in no_showcase]

    # Reports: every domain SHELF, not only the ones holding something. An
    # empty domain is a declared taxonomy, so a zero is a fact worth printing.
    reports_dir = SKILL_DIR / "reports"
    shelves = sorted(d for d in reports_dir.iterdir()
                     if d.is_dir() and not d.name.startswith(("_", ".", "__")))
    found_reports = reports()
    lines += ["", f"reports     {len(found_reports)}"]
    for shelf in shelves:
        held = [r for r in found_reports if shelf in r.parents]
        empty = "   (shelf declared, empty)" if not held else ""
        lines.append(f"  {shelf.name:<38}{len(held):>4}{empty}")

    pinned = version()
    lines += ["", f"version     {pinned.get('version', '?')}"
                  f"   every generated page pins this at BUILD time"]
    if not pinned:
        lines.append(f"      no readable {VERSION_FILE.name} at {VERSION_FILE} "
                     f"- nothing here can render a page")
    return lines


def checks() -> tuple[int, list[str]]:
    """Run every check. Returns (failures, lines to print).

    The output of a failing check is passed through rather than summarized: it
    already names the file and the command that fixes it, and a summary of it
    would be this script's own account of somebody else's finding."""
    lines, failed = ["checks"], 0

    # The two checks with no engine behind them, computed here and printed in
    # procedure order below: they cost milliseconds, so they are done before
    # anything spawns a process that renders a hundred pages.
    orphans = unbundled()
    broken = nonconforming()
    crossed = misprefixed()
    dead = unstyled()

    failed += bool(broken)
    lines.append(f"  {'usage.md skeleton':<38}"
                 f"{'ok' if not broken else 'NONCONFORMING'}")
    lines += [f"      {reason}" for reason in broken]

    failed += bool(crossed)
    lines.append(f"  {'class prefixes own their directory':<38}"
                 f"{'ok' if not crossed else 'CROSSED'}")
    lines += [f"      {reason}" for reason in crossed]

    failed += bool(dead)
    lines.append(f"  {'every class in markup is reachable':<38}"
                 f"{'ok' if not dead else 'DEAD'}")
    lines += [f"      {reason}" for reason in dead]

    for label, argv in CHECKS:
        done = subprocess.run([sys.executable, str(SKILL_DIR / argv[0]), *argv[1:]],
                              capture_output=True, text=True)
        output = (done.stdout + done.stderr).strip()
        ok = done.returncode == 0
        failed += not ok

        # A CHECK THAT COULD NOT RUN IS NOT A CHECK THAT FAILED, and saying
        # "STALE" for a missing library is the exact misleading signal this
        # file exists to prevent -- it sends someone to regenerate a catalogue
        # that is perfectly current. Every check in CHECKS imports Jinja, so a
        # system interpreter fails them all identically and the fix is one
        # thing, printed once, instead of a traceback each that never names it.
        missing = re.search(r"No module named '([^']+)'", output)
        if missing:
            lines.append(f"  {label:<38}NOT RUN")
            lines.append(f"      no {missing.group(1)} on this interpreter - "
                         f"run this with the project venv")
            continue

        lines.append(f"  {label:<38}{'ok' if ok else 'STALE'}")
        if not ok:
            lines += [f"      {line}" for line in output.splitlines() if line.strip()]

    failed += bool(orphans)
    lines.append(f"  {'bundles load every module':<38}"
                 f"{'ok' if not orphans else 'INCOMPLETE'}")
    lines += [f"      {orphan} exists but no bundle loads it" for orphan in orphans]

    return failed, lines


def main(argv: list[str] | None = None) -> int:
    """The terminal entry point.

    Plain hyphens in anything printed: stdout is cp1252 on Windows, where an
    em dash shows as a replacement character."""
    parser = argparse.ArgumentParser(
        prog="status.py",
        description="what is in this skill, and whether every generated file "
                    "is current",
        epilog=f"example: {COMMAND} --check")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if any generated file is stale "
                             "(the last step of adding a component or a report)")
    args = parser.parse_args(argv)

    print(f"finance-reports  {SKILL_DIR}")
    print()
    print("\n".join(inventory()))
    print()
    failed, lines = checks()
    print("\n".join(lines))

    if failed:
        print(f"\n{failed} check(s) failed.")
    return 1 if (failed and args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())
