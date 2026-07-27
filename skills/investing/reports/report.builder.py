"""reports — the report engine: fetch live data, shape it, render a report.

RUNNABLE ON ITS OWN. This directory builds its own reports with no reference to
../builder.py:

    python reports/report.builder.py financial-profile INTC --peers AMD --out DIR

THE SHAPE, and it is the showcase's shape exactly:

    report.master.html.j2        the shell        showcase.master.html.j2
    <name>/report.controller.py  fetch() + shape()  showcase.controller.py
    <name>/report.html.j2        the view         showcase.html.j2

A CONTROLLER BUILDS DATA. A VIEW EMITS MARKUP. The controller fetches and does
arithmetic; the view decides which components appear and in what order, and is
the only thing that calls a macro. Break that and the two stop being
replaceable.

WHERE THE ENV COMES FROM. Not from here. components/ owns the macros, the
number filters they use, and the Jinja environment that exposes them as `c` —
this file borrows it, so a macro drawn on a showcase page draws the same in a
report. The arrow points ONE WAY: reports depend on components, never the
reverse.

HOW THIS DIFFERS FROM docs-html. There, a doc-type is a SKELETON a human fills:
component calls carrying literal placeholder text, and the output is edited by
hand. Here a report is a PROGRAM: the same component calls carry `d.*`, and the
output is regenerated. The consequence is `StrictUndefined` on the shared env.

Jinja runs ONLY at build time. The written file is standalone HTML with no
Jinja left, linking the local bundle first and the version-pinned CDN second.

WHAT GUARDS THE OUTPUT. Building a report requires the network and a key, so
there is no offline check: shape()'s assertions and StrictUndefined fire during
a real build, and nowhere else.
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from types import SimpleNamespace

REPORTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPORTS_DIR.parent

SHELL = "report.master.html.j2"
CONTROLLER = "report.controller.py"
VIEW = "report.html.j2"

REPORT_NAME_RE = re.compile(r"\{#\s*report-name:\s*(.+?)\s*#\}")


def _components():
    """The components package's engine, loaded BY PATH.

    Its filename carries a dot — `showcase.builder.py`, matching this file's
    naming — so it can never be reached by `import`. Path-loading is this
    skill's idiom anyway: controllers on both sides are loaded the same way,
    and no folder here is a package or wants an __init__.py."""
    path = SKILL_DIR / "components" / "showcase.builder.py"
    spec = importlib.util.spec_from_file_location("components_showcase", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


components = _components()


class Reports:
    """Every report, and everything needed to build one.

    Holds a Showcases so the Jinja environment is built ONCE and shared: the
    same `c` namespace, the same filters, the same StrictUndefined."""

    def __init__(self, root: Path = REPORTS_DIR):
        self.root = Path(root).resolve()
        self.components = components.Showcases()

    # ---------------------------------------------------------------- find
    def all(self) -> dict[str, Path]:
        """Every report folder, discovered recursively: name -> directory.

        Same rule as components: found, never registered."""
        dirs: dict[str, Path] = {}
        for view in sorted(self.root.rglob(VIEW)):
            name = view.parent.name
            if name in dirs:
                raise SystemExit(f"duplicate report name: {name!r} "
                                 f"({dirs[name]} and {view.parent})")
            dirs[name] = view.parent
        return dirs

    def resolve(self, name: str) -> str:
        """Exact name, or the one report whose name starts with it — so
        `financial` reaches `financial-profile` and an ambiguous prefix says
        so rather than picking one."""
        names = self.all()
        if name in names:
            return name
        matches = [n for n in names if n.startswith(name)]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise SystemExit(f"unknown report: {name!r}\n"
                             f"known: {', '.join(sorted(names))}")
        raise SystemExit(f"ambiguous report {name!r}: {', '.join(sorted(matches))}")

    def controller(self, name: str):
        """Import <name>/report.controller.py by path.

        By path rather than by package, so a report folder needs no
        __init__.py and the discovery rule stays 'a directory containing
        report.html.j2'."""
        path = self.all()[name] / CONTROLLER
        if not path.exists():
            raise SystemExit(f"{name}: no {CONTROLLER} beside {VIEW}")
        spec = importlib.util.spec_from_file_location(
            f"report_{name.replace('-', '_')}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "shape"):
            raise SystemExit(f"{name}: {CONTROLLER} defines no shape()")
        return module

    # -------------------------------------------------------------- render
    def compose(self, name: str, d: dict, out_dir: Path | str,
                title: str = "") -> str:
        """Render one report's view with the data its controller produced.

        `out_dir` is where the file is about to be written, and it has NO
        DEFAULT on purpose: the head's local asset href is relative to it, so a
        report composed without naming its destination would link assets
        relative to a directory nobody chose. Whoever knows where the file is
        going passes it."""
        directory = self.all()[name]
        rel = (directory.relative_to(SKILL_DIR) / VIEW).as_posix()
        src = (SKILL_DIR / rel).read_text(encoding="utf-8")
        match = REPORT_NAME_RE.search(src)
        display = match.group(1).strip() if match else name.replace("-", " ").title()

        return self.components.env().get_template(rel).render(
            d=SimpleNamespace(**d) if isinstance(d, dict) else d,
            title=title or d.get("title", display),
            report_name=display,
            local_href=components.local_href(out_dir),
            cdn_href=components.cdn_href())

    def build(self, name: str, rest: list[str], out_dir: str,
              force: bool = False) -> int:
        """fetch() -> shape() -> render -> write."""
        name = self.resolve(name)
        module = self.controller(name)

        parser = argparse.ArgumentParser(prog=f"report.builder.py {name}")
        if hasattr(module, "add_args"):
            module.add_args(parser)
        args = parser.parse_args(rest)

        if not hasattr(module, "fetch"):
            raise SystemExit(f"{name}: {CONTROLLER} defines no fetch()")

        print("fetching …", flush=True)
        payloads = module.fetch(**vars(args))
        print("shaping and asserting …", flush=True)
        d = module.shape(payloads)

        # Resolve the destination BEFORE rendering: the head's local asset href
        # is relative to it, so the report has to know where it is going.
        out = Path(out_dir).resolve()
        html = self.compose(name, d, out)

        stem = d.get("slug") or name
        out.mkdir(parents=True, exist_ok=True)
        target = (out / f"{stem}-{name}.html" if not stem.endswith(name)
                  else out / f"{stem}.html")
        if target.exists() and not force:
            print(f"refusing to overwrite {target.name} (pass --force)")
            return 1
        target.write_text(html, encoding="utf-8")

        left = re.findall(r"\{\{[^{}]{0,60}", html)
        print(f"built: {target}")
        if left:
            print(f"  {len(left)} prose slot(s) left to fill by hand")
        return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="report.builder.py",
        description="build a report from live data")
    parser.add_argument("report", help="report name (or a unique prefix)")
    parser.add_argument("--out", required=True,
                        help="output directory — required: the report's local "
                             "asset links are relative to it")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing file")
    args, rest = parser.parse_known_args(argv)
    return Reports().build(args.report, rest, args.out, args.force)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
