"""Where the FMP key comes from — and, more importantly, where it must not be.

THIS REPOSITORY IS PUBLIC and jsDelivr's `/gh/` path publishes it, so a key
committed anywhere under it is fetchable at a URL by anyone who guesses the
path. No tracked file carries an `api_key`, and `secrets.*.json` is gitignored
with no exception.

    key:  $FMP_API_KEY  ->  <project>/secrets.<env>.json  ->  hard error
    env:  $ENVIRONMENT  ->  <project>/environment.json    ->  hard error

First hit wins, and there is deliberately no third place either looks: a skill
that reads credentials from wherever it can find them is one refactor away
from reading them from somewhere it should not.

NO DEFAULT AT ANY POINT. One declaration selects both the config file and the
secrets file, so a run cannot read dev settings against a prod key, and every
build prints what it resolved and from where before it spends a call.

The reasoning — why declared rather than passed, why two environments, why the
files sit beside .claude/ rather than inside the skill — is in
service_providers/REFERENCE.md.
"""

import json
import os
from pathlib import Path

from _paths import PROJECT_ROOT

ENV_VAR = "FMP_API_KEY"
ENV_NAME_VAR = "ENVIRONMENT"
KNOWN_ENVS = ("dev", "prod")

#: Which environment this checkout is. TRACKED, unlike the secrets it selects:
#: it holds no secret, and a name nobody reaches for by reflex is a name that
#: can be committed safely. `.env` could not — it is where every tutorial in
#: the world tells you to put an API key.
ENV_FILE = PROJECT_ROOT / "environment.json"


def _from_file() -> str:
    """`{"environment": "..."}` out of environment.json, or "".

    utf-8-sig, not utf-8: a BOM is invisible in every editor and would make the
    first key parse wrong, so the file would look right and be ignored.
    PowerShell 5.1's `Set-Content -Encoding utf8` writes one by default."""
    if not ENV_FILE.exists():
        return ""
    try:
        data = json.loads(ENV_FILE.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{ENV_FILE} is not valid JSON: {exc}") from exc
    return str(data.get(ENV_NAME_VAR.lower(), "")).strip()


def resolve() -> tuple[str, str]:
    """(environment, where it came from). NO default at any point.

    The source is returned, not just the name, because with two places to look
    the useful question is not only "which environment" but "why did it think
    so" — a stale shell variable overriding the checkout's own file is exactly
    the confusion this prevents, and the build prints the answer."""
    name = os.environ.get(ENV_NAME_VAR, "").strip()
    source = f"${ENV_NAME_VAR}"
    if not name:
        name, source = _from_file(), str(ENV_FILE)
    if not name:
        raise SystemExit(
            f"{ENV_NAME_VAR} is not set and {ENV_FILE} does not declare it. "
            f"There is no default.\n"
            f'  for this checkout :  {{"{ENV_NAME_VAR.lower()}": "dev"}}  in\n'
            f"                       {ENV_FILE}\n"
            f'  or for one shell  :  $env:{ENV_NAME_VAR} = "dev"')
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
    return PROJECT_ROOT / f"secrets.{env or environment()}.json"


def _missing(path: Path) -> str:
    return f"""No FMP credential found for environment {environment()!r}. Set one of:

  1. the {ENV_VAR} environment variable, e.g. in this shell
         $env:{ENV_VAR} = "<key>"          (PowerShell)
         export {ENV_VAR}=<key>            (bash)

  2. this file, containing {{"fmp": {{"api_key": "<key>"}}}}
         {path}
     Write it by hand — there is no template to copy, on purpose: .gitignore
     matches secrets.*.json with NO exception, so nothing by that name can be
     staged. This repository is PUBLIC. See README.md.

The environment comes from ${ENV_NAME_VAR} or {ENV_FILE}; there is no default."""


def describe() -> str:
    """WHERE the key will come from — never the key itself.

    Exists so a build can say which credential it used. The env var silently
    beating the file is the failure this prevents: a variable left over in a
    shell from some earlier command overrides secrets.prod.json with nothing
    on screen to say so. The FULL path, because two checkouts hold files of
    the same name and a basename cannot tell you which one paid."""
    if os.environ.get(ENV_VAR, "").strip():
        return f"key from ${ENV_VAR}"
    return f"key from {secrets_file()}"


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
            raise SystemExit(f"{path} is not valid JSON: {exc}") from exc
        key = (data.get("fmp") or {}).get("api_key", "").strip()
        # A `<...>` placeholder is not a key. Say so, rather than sending it to
        # the API and reporting whatever 401 comes back — the cause is three
        # directories away from the symptom.
        if key.startswith("<") and key.endswith(">"):
            raise SystemExit(
                f"{path} still holds the placeholder {key!r}. "
                f"Replace it with a real FMP key.")
        if key:
            return key

    raise SystemExit(_missing(path))
