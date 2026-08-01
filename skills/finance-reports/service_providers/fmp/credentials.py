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
                              machine. <env> is AIFX_ENV
    3. hard error naming both

THERE IS NO DEFAULT ENVIRONMENT, and that is the same decision `--out` makes
one directory over: an absent default is a question, not a gap. A default here
would mean a run can use the wrong credentials and say nothing, and the symptom
— a rate limit, a 401, a quota burned — surfaces three layers from the cause.
`report_builder.py` therefore takes `--env dev|prod` as a REQUIRED argument.
One switch selects both this file and config/config.<env>.json, so a run cannot
read dev settings against a prod key.

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
ENV_NAME_VAR = "AIFX_ENV"
KNOWN_ENVS = ("dev", "prod")


def environment() -> str:
    """Which environment this run is — `AIFX_ENV`, and there is NO default.

    Unset is an error rather than an assumption. A default would let a run use
    the wrong credentials and the wrong config silently, and nothing downstream
    can tell the difference: the request succeeds, the numbers arrive, and only
    the quota or the rate limit ever says which key paid for them.

    `report_builder.py --env dev|prod` sets this for a build, which is why a
    required flag rather than an optional one — a required argument cannot be
    forgotten, and it lands in shell history and CI logs where a variable set
    in some earlier shell does not."""
    name = os.environ.get(ENV_NAME_VAR, "").strip()
    if not name:
        raise SystemExit(
            f"{ENV_NAME_VAR} is not set, and there is no default.\n"
            f"  build a report with:  --env {'|'.join(KNOWN_ENVS)}\n"
            f"  or set it directly :  $env:{ENV_NAME_VAR} = \"dev\"")
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

  2. {path.name} at the repo root — copy the tracked template:
         cp secrets.example.json {path.name}
     then replace the placeholder. {path.name} is gitignored; the template is
     not, which is why they are two filenames and not one. This repo is PUBLIC.

The environment comes from --env or {ENV_NAME_VAR}; there is no default."""


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
