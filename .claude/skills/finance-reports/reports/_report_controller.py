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

# BORROWED, NOT REBUILT: a macro drawn on a report must link the same assets it
# links on a showcase, and two copies of the pair would be free to disagree.
from _paths import owning_directory                          # noqa: E402
from components._showcase_controller import (                # noqa: E402
    cdn_href, check_asset_bundles, env, local_href)
from reports._report_validation import NOT_YET, validate     # noqa: E402

VIEW = "report.html.j2"


def blame(exc: BaseException) -> str:
    """Which TEMPLATE raised — the part of a Jinja traceback worth printing.

    Jinja rewrites tracebacks so template frames appear as real frames whose
    filename is the .j2 path; the DEEPEST one is the culprit. A report view
    calls dozens of macros across as many components, so "something in the
    render failed" is not an answer anyone can act on."""
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

    #: What a reader sees as the document type, above the title.
    TITLE = ""

    #: The sections this report's view declares, in its order. Written out here
    #: rather than read back from the view: a check that derives its expectation
    #: from the thing it is checking agrees with it by construction, including
    #: when both are wrong. A deleted section should show up on the page and be
    #: deliberately removed from this tuple. Empty means no promise was made and
    #: the two section checks are skipped rather than invented.
    SECTIONS: tuple[str, ...] = ()

    #: The domain class prefix this report's components carry - `fa-` for a
    #: company report, `portfolio-` for a book. Empty skips the check. Zero
    #: occurrences of it in a finished page means that family did not render.
    PREFIX = ""

    # ------------------------------------------------------------- subclass
    def _expected_text(self, **args) -> list[str]:
        """Strings the request named that MUST appear in the finished page.

        OPTIONAL. Called with the same arguments as `_fetch`, because only this
        report knows its own argument shape - `financial-profile` reads a symbol
        and a comma-separated `--peers`, and the next report need not take
        either. A peer whose payload came back empty still gets its column,
        labelled and blank, so the table looks complete while comparing the
        subject against nothing; this is what notices."""
        return []

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
        """The report's folder, taken from the SUBCLASS's own file."""
        return owning_directory(self, ReportController)

    @property
    def name(self) -> str:
        """The report's identity IS its folder name."""
        return self.directory.name

    # ---------------------------------------------------------------- build
    def build(self, out_dir, asset_bundles, **args) -> Path:
        """fetch -> derive -> validate -> render -> write. Returns the file.

        `asset_bundles` is "local" or "cdn" and is NAMED, not folded into
        `**args`: those belong to the report and reach `_fetch()`, and this one
        is the engine's. A report must never see it.

        Raises rather than returning a code: a report asked for by name and
        not built is a mistake worth stopping for, and the caller owns the
        reporting.

        VALIDATION DOES NOT RAISE, and that is deliberate. By the time the page
        is checked it has already cost ~13 live calls, so throwing it away over
        a finding would charge for the diagnosis twice. The page is written
        whatever was found, the findings are rendered into the top of it, and
        the caller gets the file back."""
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
        # The asset choice is checked against it here for the same reason: a
        # combination that cannot produce a working link should cost nothing.
        out = Path(out_dir).resolve()
        check_asset_bundles(asset_bundles, out)

        print("fetching ...", flush=True)
        payloads = self._fetch(**args)

        print("deriving and asserting ...", flush=True)
        d = self._build_context(payloads)
        if not isinstance(d, dict):
            raise SystemExit(f"{self.name}: _build_context() returned "
                             f"{type(d).__name__}, expected dict")
        self._validate_context(d)

        report_name = self.TITLE or self.name
        template = env().get_template(view)

        def render(validation):
            try:
                return template.render(
                    d=SimpleNamespace(**d),
                    title=d.get("title", report_name),
                    report_name=report_name,
                    asset_bundles=asset_bundles,
                    local_href=local_href(out),
                    cdn_href=cdn_href(),
                    validation=validation)
            except Exception as e:  # noqa: BLE001 — name the template, re-raise
                raise SystemExit(f"{self.name}: render failed{blame(e)}: "
                                 f"{type(e).__name__}: {e}") from None

        html = render(NOT_YET)

        # CHECKED BEFORE THE BANNER EXISTS, which is the whole ordering. What
        # these checks measure is the document; re-rendering with the findings
        # would have them measuring the notice about the document as well.
        print("validating the render ...", flush=True)
        found = validate(html, out, asset_bundles,
                         sections=self.SECTIONS, prefix=self.PREFIX,
                         expected=self._expected_text(**args))

        # ALWAYS re-rendered, including when nothing was found. Skipping this
        # for a clean page was tried and is wrong: the page then keeps the
        # placeholder's counts and its all-clear reads "0 check(s)", which is
        # precisely the "did validation even run?" ambiguity the comment exists
        # to remove. A second render costs milliseconds against a cached
        # environment and no network at all.
        html = render(found)

        # Overwritten without asking: the output is a build artifact, and the
        # controller and the view are the source.
        out.mkdir(parents=True, exist_ok=True)
        target = out / self._filename(d)
        target.write_text(html, encoding="utf-8")

        # Said on the way out as well as shown on the page. The page is where a
        # reader meets it; a caller building ten reports wants the count without
        # opening ten files. NOT raised: the page cost ~13 live calls and is
        # written either way, and a broken page you can open beats an exception.
        for problem in found.errors:
            print(f"  ERROR    {problem.check}: {problem.message}", flush=True)
        for problem in found.warnings:
            print(f"  warning  {problem.check}: {problem.message}", flush=True)
        return target
