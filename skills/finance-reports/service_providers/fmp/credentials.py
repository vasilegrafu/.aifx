"""Where the FMP key comes from — and, more importantly, where it must not be.

THIS REPOSITORY IS PUBLIC. `aifx-finance` is served by jsDelivr, whose `/gh/`
path only publishes public GitHub repos, so a key committed anywhere under
this directory is not merely "in a repo" — it is fetchable at a URL by anyone
who guesses the path. That is why no tracked file in this repo carries an
`api_key` value and why `secrets.*.json` is in `.gitignore`.

Resolution order, first hit wins:

    1. FMP_API_KEY            environment variable — preferred, and the only
                              option that works in CI, where there is no file
    2. secrets.<env>.json     at the REPO ROOT, gitignored, never leaves the
                              machine. <env> is ENVIRONMENT
    3. hard error naming both

THERE IS NO DEFAULT ENVIRONMENT, and no flag either. It is declared in the
environment, in one of exactly two places:

    1. ENVIRONMENT        the variable — set by a shell, by CI, or by setx
    2. .env               at the REPO ROOT, gitignored: `ENVIRONMENT=dev`,
                          a property of THIS checkout on THIS machine
    3. hard error

A CLI flag was tried and removed. It could only reach builds driven through
`report_builder.py`, while anything importing FmpClient directly still needed
the variable — so the same fact had two homes and they could disagree. And a
flag cannot be inherited: an editor's terminal settings do not reach a shell
spawned by another tool, which is exactly where the builds actually run.

An absent default is a question, not a gap — the same decision `--out` makes
one directory over. A default would let a run use the wrong credentials and say
nothing, and the symptom (a rate limit, a 401, a quota burned) surfaces three
layers from the cause. `.env` is not a default: someone wrote it, it names one
checkout, and every build prints which source it came from.

One declaration selects both this file and config/config.<env>.json, so a run
cannot read dev settings against a prod key.

THE SECRETS FILES LIVE AT THE REPO ROOT, NOT IN THIS DIRECTORY, and that is
deliberate. A skill is meant to be copied or junctioned into another project —
`skills/finance-reports/` and nothing above it. Keeping the key outside that
subtree means copying the skill cannot carry a credential with it. Its
non-secret twin, config/config.<env>.json, sits beside it; see config.py for
why the split is per-FILE rather than per-field.

Two environments rather than one because a dev key and a production key have
different rate limits and different blast radii, and the way that goes wrong is
someone burning a production quota on a test run.

There is deliberately no option that reaches into another project's config
file. A skill that silently reads credentials from wherever it can find them is
one refactor away from reading them from somewhere it should not.
"""

import json
import os
from pathlib import Path

#: skills/<name>/service_providers/fmp/credentials.py -> the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]

ENV_VAR = "FMP_API_KEY"
ENV_NAME_VAR = "ENVIRONMENT"
KNOWN_ENVS = ("dev", "prod")

#: Machine-local declaration of which environment this checkout is.
DOTENV = REPO_ROOT / ".env"


def _from_dotenv() -> str:
    """`ENVIRONMENT=...` out of .env, or "" — deliberately not a dotenv parser.

    It reads ONE key and understands `KEY=value`, `#` comments and blank lines.
    Nothing here wants export syntax, interpolation or multi-line values, and a
    fuller parser would invite putting things in this file that belong in
    config/ (not secret) or secrets.<env>.json (secret)."""
    if not DOTENV.exists():
        return ""
    # utf-8-sig, not utf-8: a BOM is invisible in every editor and would make
    # the first key read as "﻿ENVIRONMENT", which matches nothing and
    # reports as "not declared" — the file looks right and is ignored.
    # PowerShell 5.1's `Set-Content -Encoding utf8` writes one by default.
    for line in DOTENV.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep and key.strip() == ENV_NAME_VAR:
            return value.strip().strip('"').strip("'")
    return ""


def resolve() -> tuple[str, str]:
    """(environment, where it came from). NO default at any point.

    The source is returned, not just the name, because with two places to look
    the useful question is not only "which environment" but "why did it think
    so" — a stale shell variable overriding the checkout's own .env is exactly
    the confusion this prevents, and the build prints the answer."""
    name = os.environ.get(ENV_NAME_VAR, "").strip()
    source = f"${ENV_NAME_VAR}"
    if not name:
        name, source = _from_dotenv(), DOTENV.name
    if not name:
        raise SystemExit(
            f"{ENV_NAME_VAR} is not set and {DOTENV.name} does not declare it. "
            f"There is no default.\n"
            f"  for this checkout :  write {DOTENV.name} at the repo root "
            f"containing  {ENV_NAME_VAR}=dev\n"
            f"  or for one shell  :  $env:{ENV_NAME_VAR} = \"dev\"")
    if name not in KNOWN_ENVS:
        raise SystemExit(
            f"{ENV_NAME_VAR}={name!r} (from {source}) is not one of "
            f"{', '.join(KNOWN_ENVS)}.")
    return name, source


def environment() -> str:
    """Which environment this run is."""
    return resolve()[0]


def secrets_file(env: str | None = None) -> Path:
    """Path to the secrets file for `env` (default: the selected one)."""
    return REPO_ROOT / f"secrets.{env or environment()}.json"


def _missing(path: Path) -> str:
    return f"""No FMP credential found for environment {environment()!r}. Set one of:

  1. the {ENV_VAR} environment variable, e.g. in this shell
         $env:{ENV_VAR} = "<key>"          (PowerShell)
         export {ENV_VAR}=<key>            (bash)

  2. {path.name} at the repo root, containing
         {{"fmp": {{"api_key": "<key>"}}}}
     Write it by hand — there is no template to copy, on purpose: .gitignore
     matches secrets.*.json with NO exception, so nothing by that name can be
     staged. This repository is PUBLIC. See README.md.

The environment comes from {ENV_NAME_VAR} or {DOTENV.name}; there is no default."""


def describe() -> str:
    """WHERE the key will come from — never the key itself.

    Exists so a build can say which credential it used. The env var silently
    beating the file is the failure this prevents: a variable left over in a
    shell from some earlier command overrides secrets.prod.json with nothing
    on screen to say so."""
    if os.environ.get(ENV_VAR, "").strip():
        return f"key from ${ENV_VAR}"
    return f"key from {secrets_file().name}"


def api_key() -> str:
    """The FMP key, or a hard error explaining how to provide one."""
    from_env = os.environ.get(ENV_VAR, "").strip()
    if from_env:
        return from_env

    path = secrets_file()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path.name} is not valid JSON: {exc}") from exc
        key = (data.get("fmp") or {}).get("api_key", "").strip()
        # The placeholder the tracked template ships with is not a key. Say so,
        # rather than sending it to the API and reporting whatever 401 comes
        # back — the cause is three directories away from the symptom.
        if key.startswith("<") and key.endswith(">"):
            raise SystemExit(
                f"{path.name} still holds the placeholder {key!r}. "
                f"Replace it with a real FMP key.")
        if key:
            return key

    raise SystemExit(_missing(path))
