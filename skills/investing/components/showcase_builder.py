import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, StrictUndefined

COMPONENTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = COMPONENTS_DIR.parent

# `import filters` has to work whether this file is RUN (sys.path[0] is
# components/ already) or IMPORTED as components.showcase_builder (sys.path[0]
# is the skill root). One guarded insert covers both, and it is the same idiom
# reports/report_builder.py uses to reach components in the first place.
if str(COMPONENTS_DIR) not in sys.path:
    sys.path.insert(0, str(COMPONENTS_DIR))

from filters import FILTERS                              # noqa: E402

MARKUP = "component.html.j2"        # what makes a directory a component
CONTROLLER = "showcase_controller.py"
VIEW = "showcase.html.j2"


# --------------------------------------------------------------------------
# the component library
# --------------------------------------------------------------------------

def _blame(exc: BaseException) -> str:
    """Which TEMPLATE actually raised — the part of a Jinja traceback worth
    printing. Jinja rewrites tracebacks so template frames appear as real
    frames whose filename is the .j2 path; the DEEPEST one is the culprit."""
    import traceback
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if f.filename.endswith(".j2")]
    if not frames:
        return ""
    deepest = frames[-1]
    return f" [{Path(deepest.filename).parent.name}:{deepest.lineno}]"


def cdn_href() -> str:
    """CDN prefix (version-pinned) — the FALLBACK half of the asset pair.

    Read from version.json at build time, so every generated file is pinned to
    the design-system version it was built against. Published tags are
    immutable, so a page that has left the tree keeps rendering as it did."""
    info = json.loads((SKILL_DIR.parent.parent / "version.json")
                      .read_text(encoding="utf-8"))
    cdn, version = info.get("cdn"), info["version"]
    if not cdn:
        sys.exit('version.json has no "cdn" — every page links it; set it first.')
    return cdn.replace("{version}", version).replace("{skill}", SKILL_DIR.name)


def local_href(out_dir: Path) -> str:
    """Path back to the skill FROM WHERE THE PAGE IS WRITTEN — the local half
    of the asset pair (css/css.loader.html.j2 and js/js.loader.html.j2).

    A showcase lands beside its component, three or four folders deep, and the
    page cannot know how deep that is. Whoever is about to write it does.

    Empty when no relative path exists — a different Windows drive — and the
    template then links the CDN alone rather than an href that cannot resolve."""
    try:
        return Path(os.path.relpath(SKILL_DIR, Path(out_dir).resolve())).as_posix()
    except ValueError:
        return ""


# --------------------------------------------------------------------------
# what both engines do identically
# --------------------------------------------------------------------------
#
# reports/report_builder.py imports these. They are plain functions rather than
# a base class on purpose: a base would have to live somewhere, and either
# components/ imports from outside itself — losing the self-containment that is
# the point of this directory — or it owns a generic "engine" concept that has
# nothing to do with components. Two functions cost neither, and each engine
# still reads on its own.

def resolve_name(name: str, names, kind: str, alias=None) -> str:
    """A name, an alias of one, or the single name it is a prefix of.

    So `build financial` reaches financial-profile and `showcase bar_negative`
    reaches bar-negative. An ambiguous prefix says which ones it matched rather
    than picking the first."""
    names = list(names)
    if name in names:
        return name
    if alias:
        for known in names:
            if alias(known) == name:
                return known
    matches = [n for n in names if n.startswith(name)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"unknown {kind}: {name!r}\n"
                         f"known: {', '.join(sorted(names))}")
    raise SystemExit(f"ambiguous {kind} {name!r}: {', '.join(sorted(matches))}")


def load_controller(path: Path, alias: str, requires: str):
    """Path-load one controller and check it honours its contract.

    By path rather than by package, so an item folder needs no __init__.py and
    the discovery rule stays 'a directory containing the markup'. Both sides
    load the same way; only the function they require differs — shape() for a
    report, context() for a showcase."""
    if not path.exists():
        raise SystemExit(f"{path.parent.name}: no {path.name}")
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, requires):
        raise SystemExit(f"{path.parent.name}: {path.name} defines no {requires}()")
    return module


class Showcases:
    """The component library, and everything needed to show it.

    Holds the Jinja environment so it is built ONCE. That matters: building it
    parses every component template in the tree, and the old free-function form
    rebuilt it on each render because nothing owned it."""

    def __init__(self, root: Path = COMPONENTS_DIR):
        self.root = Path(root).resolve()
        self._env: Environment | None = None
        self._all: dict[str, Path] | None = None

    # ---------------------------------------------------------------- find
    def all(self) -> dict[str, Path]:
        """Every component, discovered recursively: name -> directory.

        Same shape reports/report_builder.py returns, so resolve() is the same
        function on both sides rather than a similar one.

        Cached for the same reason the env is: a scan walks the whole tree, and
        env(), showable() and write() each want it. A process that added a
        component to disk mid-run would not see it, which no CLI invocation
        does.

        components/ is organized in CATEGORY folders that exist purely for
        humans — a component's identity stays its own folder name (macro = name
        with - -> _), so category moves never touch templates. Names must be
        unique across categories."""
        if self._all is not None:
            return self._all
        dirs: dict[str, Path] = {}
        for markup in sorted(self.root.rglob(MARKUP)):
            name = markup.parent.name
            if name in dirs:
                raise SystemExit(f"duplicate component name: {name!r} "
                                 f"({dirs[name]} and {markup.parent})")
            dirs[name] = markup.parent
        self._all = dirs
        return dirs

    @staticmethod
    def macro(name: str) -> str:
        """`metric-trend` is the folder; `metric_trend` is what a view calls."""
        return name.replace("-", "_")

    def resolve(self, name: str) -> str:
        """Folder name, macro name, or a unique prefix of either."""
        return resolve_name(name, self.all(), "component", alias=self.macro)

    def showable(self) -> tuple[list[str], list[str]]:
        """Components that ship BOTH halves, and complaints about the rest.

        A component with a controller and no view (or the reverse) is half
        written. Skipping it silently is how it stays half written, so it comes
        back as a complaint the caller prints."""
        ready, half = [], []
        for name, directory in self.all().items():
            has_controller = (directory / CONTROLLER).exists()
            has_view = (directory / VIEW).exists()
            if has_controller and has_view:
                ready.append(name)
            elif has_controller:
                half.append(f"{name}: has {CONTROLLER} but no {VIEW}")
            elif has_view:
                half.append(f"{name}: has {VIEW} but no {CONTROLLER}")
        return ready, half

    # ----------------------------------------------------------------- env
    def env(self) -> Environment:
        """Built once, then reused.

        StrictUndefined IS THE POINT. A view reading a key its controller never
        produced would, by default, render an empty string — a tidy blank cell
        in an otherwise perfect table, which nobody notices. That is the same
        failure class as an unbalanced sankey: it draws beautifully and lies.
        With StrictUndefined it raises at build time instead, and since Jinja
        runs only at build time the failure costs nothing and reaches no
        reader.

        Both roots are search paths, components/ FIRST — see the module note."""
        if self._env is not None:
            return self._env
        env = Environment(
            loader=FileSystemLoader([str(self.root), str(SKILL_DIR)]),
            trim_blocks=True, lstrip_blocks=True,
            keep_trailing_newline=True, autoescape=False,
            undefined=StrictUndefined)
        env.filters.update(FILTERS)

        c = SimpleNamespace()
        for name, directory in self.all().items():
            macro = self.macro(name)
            module = env.get_template(
                (directory / MARKUP).relative_to(self.root).as_posix()).module
            if hasattr(module, macro):
                setattr(c, macro, getattr(module, macro))
        env.globals["c"] = c    # templates call {{ c.<macro>(…) }} — no imports
        self._env = env
        return env

    # -------------------------------------------------------------- render
    def controller(self, name: str):
        """<name>/showcase_controller.py, path-loaded, honouring context()."""
        return load_controller(self.all()[name] / CONTROLLER,
                               f"showcase_{self.macro(name)}", "context")

    def compose(self, name: str) -> str:
        """Render one component's view with the data its controller produced.

        Nothing here calls a macro. The view does, through the same `c`
        namespace and the same env a report uses.

        A showcase always lands beside its component, so unlike a report it has
        no destination to be told — the asset hrefs follow from where it goes."""
        directory = self.all()[name]
        d = self.controller(name).context()
        if not isinstance(d, dict):
            raise SystemExit(f"{name}: context() returned "
                             f"{type(d).__name__}, expected dict")
        view = (directory / VIEW).relative_to(self.root).as_posix()

        return self.env().get_template(view).render(
            d=SimpleNamespace(**d),
            title=f"{name} — showcase",
            component_name=name,
            local_href=local_href(directory),
            cdn_href=cdn_href())

    def write(self, name: str | None = None) -> int:
        """Write showcase.html beside every component that ships both halves.

        The output is a build artifact: this is a PUBLIC repo and 109 generated
        pages have no business being served by the CDN. Regenerate them locally
        to browse; the controller and the view are the source."""
        ready, half = self.showable()
        if name:
            wanted = self.resolve(name)
            if wanted not in ready:
                print(f"{wanted}: no {CONTROLLER} + {VIEW} to show")
                for complaint in half:
                    print(f"  {complaint}")
                return 1
            ready = [wanted]

        for item in ready:
            out = self.all()[item] / "showcase.html"
            try:
                out.write_text(self.compose(item), encoding="utf-8")
            except Exception as e:          # noqa: BLE001 — report, don't crash
                print(f"  {item:<30} FAILED{_blame(e)}: "
                      f"{type(e).__name__}: {e}")
                return 1
            print(f"composed: {out.relative_to(SKILL_DIR)}")

        if not ready and not name:
            print(f"no showcases yet — add {CONTROLLER} + {VIEW} "
                  f"beside a {MARKUP}")
        for complaint in half:
            print(f"  half-written — {complaint}")
        return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="showcase_builder.py",
        description="render each component's showcase.html from its controller + view")
    parser.add_argument("name", nargs="?",
                        help="only this component (folder or macro name)")
    args = parser.parse_args(argv)
    return Showcases().write(args.name)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
