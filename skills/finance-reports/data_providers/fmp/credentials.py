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
                              machine. <env> is AIFX_ENV, default "dev"
    3. hard error naming both

THE SECRETS FILES LIVE AT THE REPO ROOT, NOT IN THIS DIRECTORY, and that is
deliberate. A skill is meant to be copied or junctioned into another project —
`skills/finance-reports/` and nothing above it. Keeping the key outside that
subtree means copying the skill cannot carry a credential with it.

Two environments rather than one because a dev key and a production key have
different rate limits and different blast radii, and the way that goes wrong is
someone burning a production quota on a test run. Selecting between them with
an environment variable rather than a flag keeps it out of every command line —
a flag is something you can forget on the one invocation that matters.

There is deliberately no option that reaches into another project's config
file. A skill that silently reads credentials from wherever it can find them is
one refactor away from reading them from somewhere it should not.
"""

import json
import os
from pathlib import Path

#: skills/<name>/data_providers/fmp/credentials.py -> the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]

ENV_VAR = "FMP_API_KEY"
ENV_NAME_VAR = "AIFX_ENV"
DEFAULT_ENV = "dev"
KNOWN_ENVS = ("dev", "prod")


def environment() -> str:
    """Which secrets file to read — `AIFX_ENV`, defaulting to dev.

    Defaults to dev on purpose: the safe one. An unset variable should not
    reach production credentials, and a typo should not silently fall back to
    them either, which is why an unknown value is an error rather than a
    default."""
    name = os.environ.get(ENV_NAME_VAR, "").strip() or DEFAULT_ENV
    if name not in KNOWN_ENVS:
        raise SystemExit(
            f"{ENV_NAME_VAR}={name!r} is not one of {', '.join(KNOWN_ENVS)}.")
    return name


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
     (already in .gitignore — this repo is PUBLIC, so never commit a key)

Switch environments with {ENV_NAME_VAR}=dev|prod (default {DEFAULT_ENV})."""


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
