"""Run the reports' tests, discovered rather than listed.

    python .claude/skills/finance-reports/reports/report_test_runner.py --list   what exists, and cost
    python .claude/skills/finance-reports/reports/report_test_runner.py financial-profile
    python .claude/skills/finance-reports/reports/report_test_runner.py --all

NOTHING IS REGISTERED, and it is the same rule twice over. A directory holding
`report.html.j2` IS a report; one that also holds `report_test.py` HAS a test -
exactly as a component directory holding `showcase_controller.py` has a
showcase. Adding a test means adding a file beside the report and telling
nothing. The name is the report's own, so `financial-profile` is what you type
whichever engine you are talking to.

THE TWIN OF report_builder.py, and deliberately shaped like it: discovery by
walking, a report addressed by NAME rather than by path, and a refusal on a
duplicate rather than a guess. `reports/` owns the engine for what lives in
`reports/`, which is why this is here and not at the skill root - there is still
no top-level dispatcher, and `components/` would own its own.

WHY `--all` IS EXPLICIT, and the whole reason this file is careful. Every test
builds its report against the live API - roughly 13 calls each, nothing cached,
no fixture and no offline mode. Ten reports is a hundred and thirty calls of
real quota, so a bare invocation runs NOTHING and prints what it would have
cost. `components/showcase_builder.py --all` carries the same warning for the
same reason; there the stake is a stale page, here it is a bill.

EACH TEST IS ITS OWN PROCESS. They are isolated by construction that way: every
one puts the skill on `sys.path` and path-loads controllers into `sys.modules`
under aliases of its own, and the exit code is already the contract. Sharing an
interpreter would trade that for about half a second of cached Jinja
environment, against a test that spends ten seconds on the network.
"""

import argparse
import ast
import subprocess
import sys
import time
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent

TEST = "report_test.py"
VIEW = "report.html.j2"


def discover() -> dict[str, Path]:
    """Every report test: name -> the file. Found, never registered.

    Walks for the TEST rather than for the view and then looking beside it, so
    a report with no test is simply absent instead of being an error - most
    reports will have one, and the ones that do not are found by `--missing`
    being obvious from `--list`."""
    found: dict[str, Path] = {}
    for test in sorted(REPORTS_DIR.rglob(TEST)):
        name = test.parent.name
        if name in found:
            raise SystemExit(f"duplicate test name: {name!r} "
                             f"({found[name]} and {test})")
        found[name] = test
    return found


def untested() -> list[str]:
    """Reports with a view and no test beside it. Worth saying out loud."""
    return sorted(view.parent.name for view in REPORTS_DIR.rglob(VIEW)
                  if not (view.parent / TEST).exists())


def cost(test: Path) -> int | None:
    """What the test says it spends, read WITHOUT running or importing it.

    Parsed out of the source as a literal `CALLS = <int>`. Reading it any other
    way would mean importing the module to ask how expensive it is, and the
    import is where the expense begins. A test that declares nothing is reported
    as unknown rather than as free."""
    try:
        tree = ast.parse(test.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CALLS"
                for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return None
            return value if isinstance(value, int) else None
    return None


def run(name: str, test: Path) -> bool:
    """One test, one process. True if it passed.

    Output is captured and shown only on failure - ten passing tests should read
    as ten lines, and a failing one should carry everything it said. The built
    page is in the report's own report_test_output/ either way."""
    print(f"  {name} ... ", end="", flush=True)
    started = time.monotonic()
    done = subprocess.run([sys.executable, str(test)],
                          capture_output=True, text=True)
    elapsed = time.monotonic() - started
    passed = done.returncode == 0
    print(f"{'PASS' if passed else 'FAIL'}  ({elapsed:.0f}s)")
    if not passed:
        for line in (done.stdout + done.stderr).splitlines():
            print(f"      | {line}")
    return passed


def main(argv: list[str] | None = None) -> int:
    """Plain hyphens in anything printed: stdout is cp1252 on Windows."""
    parser = argparse.ArgumentParser(
        prog="report_test_runner.py",
        description="run the reports' tests - each builds its report for real",
        epilog="a bare invocation runs nothing: every test spends live API "
               "calls, so the selection has to be said out loud")
    parser.add_argument("names", nargs="*",
                        help="reports to test, by name (see --list)")
    parser.add_argument("--all", action="store_true",
                        help="test every report. NOT a convenience - see cost")
    parser.add_argument("--list", action="store_true",
                        help="what exists and what it costs. Runs nothing")
    args = parser.parse_args(argv)

    tests = discover()
    if not tests:
        print(f"no {TEST} beside any report under {REPORTS_DIR}")
        return 0

    def spend(chosen):
        known = [cost(tests[n]) for n in chosen]
        total = sum(c for c in known if c)
        return f"~{total} API calls" + (" or more" if None in known else "")

    if args.list or not (args.names or args.all):
        print(f"{len(tests)} report test(s):\n")
        for name, test in tests.items():
            calls = cost(test)
            print(f"  {name:24} {test.relative_to(REPORTS_DIR).as_posix():48} "
                  f"{f'~{calls} calls' if calls else 'cost not declared'}")
        if missing := untested():
            print(f"\nno test yet: {', '.join(missing)}")
        print(f"\nall of them: {spend(tests)}. Nothing is cached and there is "
              f"no offline mode.")
        if not (args.names or args.all):
            print("Name one, or pass --all. A bare run does nothing on purpose.")
        return 0

    chosen = list(tests) if args.all else args.names
    if unknown := [n for n in chosen if n not in tests]:
        raise SystemExit(f"unknown test(s): {', '.join(unknown)}\n"
                         f"known: {', '.join(tests)}")

    print(f"running {len(chosen)} test(s), {spend(chosen)}:\n")
    failed = [name for name in chosen if not run(name, tests[name])]

    print()
    if failed:
        print(f"FAILED - {len(failed)} of {len(chosen)}: {', '.join(failed)}")
        return 1
    print(f"PASSED - {len(chosen)} of {len(chosen)}. Every page is valid; that "
          f"is not the same as right. Open them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
