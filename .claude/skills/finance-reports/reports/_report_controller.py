"""The base every report controller extends.

CONTRACT — a subclass writes two methods and may write three more:

    class FinancialProfileReportController(ReportController):
        TITLE = "Financial Profile"

        def _add_args(self, parser): ...          # optional, this report's CLI
        def _fetch(self, **args): ...             # required, the ONLY I/O
        def _build_context(self, payloads): ...   # required, pure
        def _validate_context(self, d): ...       # optional
        def _filename(self, d): ...               # optional

    FinancialProfileReportController().build(out_dir) -> Path to the .html

FOUR STAGES THAT FAIL DIFFERENTLY, and the whole shape follows from keeping
them apart:

    arguments -> fetch (I/O) -> derive (pure) -> render -> write

`_fetch` is the only thing that touches the network. `_build_context` is a pure
payloads -> dict, which is what makes the identities it asserts readable on
their own: everything they check is in front of you, with no request in the
middle. The view is handed the dict as `d` and is the only thing that calls a
macro.

THE TWIN OF components/_showcase_controller.py, differing exactly where a
report differs from a showcase: a showcase's inputs are literal and its
destination is implied, so it needs neither a fetch nor an --out. Everything
extra here is a consequence of that one sentence.
"""

import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

REPORTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = REPORTS_DIR.parent

# The skill root on the path so `components` resolves PACKAGE-QUALIFIED. Same
# reason the leaf controllers do it: reached under two names the library would
# be two module objects, and each copy would build its own cached env.
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

# BORROWED, NOT REBUILT — the same reason env() is. A macro drawn on a report
# has to link the same assets it links on a showcase, and two copies of the
# pair would be two claims about that, free to disagree. (They were, and did:
# the two had already drifted apart in their error strings.)
#
# `local_href` is why --out is required and has no default: a report can be
# written anywhere, and the href back to css/ and js/ depends entirely on
# where. See reports/REFERENCE.md.
from components._showcase_controller import (                # noqa: E402
    cdn_href, env, local_href)

VIEW = "report.html.j2"


def blame(exc: BaseException) -> str:
    """Which TEMPLATE raised — the part of a Jinja traceback worth printing.

    Jinja rewrites tracebacks so template frames appear as real frames whose
    filename is the .j2 path; the DEEPEST one is the culprit. A report view
    calls 25 macros across 15 components, so "something in the render failed"
    is not an answer anyone can act on."""
    frames = [f for f in traceback.extract_tb(exc.__traceback__)
              if f.filename.endswith(".j2")]
    if not frames:
        return ""
    deepest = frames[-1]
    return f" [{Path(deepest.filename).parent.name}:{deepest.lineno}]"


class ReportController:
    """Build one report. Subclass, write _fetch and _build_context, call build().

    Nothing here is report-specific, so nothing here needs overriding beyond
    the hooks.
    """

    #: What a reader sees as the document type, above the title. A class
    #: attribute rather than a {# report-name: … #} comment scraped out of the
    #: template source: Jinja discards comments before rendering, so reading
    #: one means parsing the file you are about to render, as text, with a
    #: regex. Declared here it is simply available.
    TITLE = ""

    # ------------------------------------------------------------- subclass
    def _add_args(self, parser) -> None:
        """Declare this report's CLI arguments on a parser the builder owns.

        OPTIONAL. A report that needs no arguments does not define it."""

    def _fetch(self, **args) -> dict:
        """THE ONLY I/O. Return raw payloads; derive nothing here."""
        raise NotImplementedError(
            f"{type(self).__name__} defines no _fetch()")

    def _build_context(self, payloads) -> dict:
        """Pure. The view model, reaching report.html.j2 as `d`.

        Where the assertions live, because this is the only place with the
        arithmetic: a diagram that does not conserve draws perfectly and lies,
        and no template and no reader can catch it."""
        raise NotImplementedError(
            f"{type(self).__name__} defines no _build_context()")

    def _validate_context(self, d: dict) -> None:
        """Assert the context matches what the view reads. Raise, return None.

        OPTIONAL, and it does the half StrictUndefined cannot. A key the view
        reads and the controller never wrote already raises at render. What
        does not is a key present and WRONG."""

    def _filename(self, d: dict) -> str:
        """What the file is called. Override when the data names it."""
        return f"{self.name}.html"

    # ---------------------------------------------------------------- where
    @property
    def directory(self) -> Path:
        """The report's folder, taken from the SUBCLASS's own file.

        Read off the function that subclass wrote — not __file__, which names
        this base module, and not inspect.getfile(cls), which resolves a class
        through sys.modules[cls.__module__] and so raises for a controller
        loaded BY PATH, since importlib registers nothing. A code object
        carries its filename with it and needs no such lookup."""
        for klass in type(self).__mro__:
            if klass is ReportController:
                break               # reached the base without finding one
            own = klass.__dict__.get("_build_context")
            if own is not None:
                return Path(own.__code__.co_filename).resolve().parent
        raise NotImplementedError(
            f"{type(self).__name__} defines no _build_context()")

    @property
    def name(self) -> str:
        """The report's identity IS its folder name."""
        return self.directory.name

    # ---------------------------------------------------------------- build
    def build(self, out_dir, **args) -> Path:
        """fetch -> derive -> validate -> render -> write. Returns the file.

        Raises rather than returning a code: a report asked for by name and
        not built is a mistake worth stopping for, and the caller owns the
        reporting."""
        directory = self.directory
        try:
            view = (directory / VIEW).relative_to(SKILL_DIR).as_posix()
        except ValueError:
            raise SystemExit(f"{type(self).__name__}: {directory} is not under "
                             f"{SKILL_DIR}") from None
        if not (directory / VIEW).exists():
            raise SystemExit(f"{self.name}: no {VIEW} beside the controller")

        # Resolved BEFORE the fetch, so a bad destination costs no network
        # calls, and before the render, because the asset href depends on it.
        out = Path(out_dir).resolve()

        print("fetching ...", flush=True)
        payloads = self._fetch(**args)

        print("deriving and asserting ...", flush=True)
        d = self._build_context(payloads)
        if not isinstance(d, dict):
            raise SystemExit(f"{self.name}: _build_context() returned "
                             f"{type(d).__name__}, expected dict")
        self._validate_context(d)

        report_name = self.TITLE or self.name
        try:
            html = env().get_template(view).render(
                d=SimpleNamespace(**d),
                title=d.get("title", report_name),
                report_name=report_name,
                local_href=local_href(out),
                cdn_href=cdn_href())
        except Exception as e:      # noqa: BLE001 — name the template, re-raise
            raise SystemExit(f"{self.name}: render failed{blame(e)}: "
                             f"{type(e).__name__}: {e}") from None

        # Overwritten without asking. The output is a BUILD ARTIFACT, the same
        # as a showcase page: the controller and the view are the source, and
        # a report regenerated from the same symbol is the same report with
        # newer numbers. Nothing here is edited by hand, so there is nothing
        # to protect.
        out.mkdir(parents=True, exist_ok=True)
        target = out / self._filename(d)
        target.write_text(html, encoding="utf-8")
        return target
