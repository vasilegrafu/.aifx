"""Build a component's showcase page, addressed by its DIRECTORY PATH.

    ShowcaseBuilder().build("charts/bar")  ->  Path to showcase.html

    python components/showcase_builder.py charts/bar

A path rather than a name, because that is the whole address: it says where
the controller is, where the view is, and where the page goes. Nothing here
holds a registry, and nothing has to be listed before it can be built — a
directory with a controller and a view IS a showcase.

The builder finds the controller class rather than being told its name.
`charts/bar` holding ChartBarShowcaseController is a convention worth keeping,
but deriving one from the other would make the convention load-bearing, and a
category that pluralizes (charts -> Chart) already shows how that goes wrong.
A subclass of ShowcaseController in the module is unambiguous.

The class does the finding; ShowcaseController.build() does the rendering, and
this file never touches Jinja — which is what keeps a controller runnable on
its own, with or without this.
"""

import argparse
import importlib.util
import sys
from pathlib import Path

COMPONENTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = COMPONENTS_DIR.parent

# PACKAGE-QUALIFIED, and the skill root on the path to make it resolve. It has
# to match how a leaf controller imports the base: reached under two different
# names, the base would be two module objects, `issubclass` below would fail
# against the wrong one, and each copy would build its own cached env.
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from components._showcase_controller import (          # noqa: E402
    MARKUP, VIEW, ShowcaseController)

CONTROLLER = "showcase_controller.py"


class ShowcaseBuilder:

    def build(self, path: str) -> Path:
        """Render the showcase at `path` — "charts/bar" — and return the page.

        Raises rather than returning a code: a showcase asked for by name and
        not built is a mistake worth stopping for."""
        directory = (COMPONENTS_DIR / path).resolve()
        try:
            directory.relative_to(COMPONENTS_DIR)
        except ValueError:
            raise SystemExit(f"{path}: outside {COMPONENTS_DIR}") from None
        if not directory.is_dir():
            raise SystemExit(f"{path}: no such directory")
        for required in (MARKUP, CONTROLLER, VIEW):
            if not (directory / required).exists():
                raise SystemExit(f"{path}: no {required}")

        return self._controller(directory)().build()

    @staticmethod
    def _controller(directory: Path) -> type[ShowcaseController]:
        """Path-load <directory>/showcase_controller.py and return the class.

        By path rather than by import, so a component folder needs no
        __init__.py and the rule stays "a directory containing the markup".
        Registered in sys.modules under its own name because a module that
        path-loads without one is invisible to anything that resolves a class
        back to its file."""
        source = directory / CONTROLLER
        name = f"showcase_{directory.relative_to(COMPONENTS_DIR)}".replace("\\", "_")
        name = name.replace("/", "_").replace("-", "_")

        spec = importlib.util.spec_from_file_location(name, source)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

        found = [value for value in vars(module).values()
                 if isinstance(value, type)
                 and issubclass(value, ShowcaseController)
                 and value is not ShowcaseController]
        if not found:
            raise SystemExit(f"{directory.name}: {CONTROLLER} defines no "
                             f"ShowcaseController subclass")
        if len(found) > 1:
            raise SystemExit(f"{directory.name}: {CONTROLLER} defines "
                             f"{len(found)} controllers: "
                             f"{', '.join(c.__name__ for c in found)}")
        return found[0]


def main(argv: list[str] | None = None) -> int:
    """The terminal entry point.

    Separate from build() so the CLI concern — parsing, printing, an exit code
    — stays out of the method a caller in Python wants, which returns a Path
    and raises. Takes argv as an argument so it is callable as main([...]) too,
    rather than only through sys.argv."""
    parser = argparse.ArgumentParser(
        prog="showcase_builder.py",
        description="render a component's showcase.html from its controller "
                    "and view",
        epilog="example: python components/showcase_builder.py charts/bar")
    # Plain hyphens in anything PRINTED: stdout is cp1252 on Windows, where an
    # em dash encodes to 0x97 and the console shows a replacement character.
    # Docstrings keep theirs — those are read in an editor, which is UTF-8.
    parser.add_argument("path",
                        help="component directory, relative to components/ "
                             "- e.g. charts/bar")
    args = parser.parse_args(argv)

    print(ShowcaseBuilder().build(args.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
