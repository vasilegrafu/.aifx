"""Where the FMP key comes from — and, more importantly, where it must not be.

THIS REPOSITORY IS PUBLIC. `aifx-finance` is served by jsDelivr, whose `/gh/`
path only publishes public GitHub repos, so a key committed anywhere under
this directory is not merely "in a repo" — it is fetchable at a URL by anyone
who guesses the path. That is why there is no `api_key` field anywhere in this
skill's tracked files and why `credentials.local.json` is in `.gitignore`.

Resolution order, first hit wins:

    1. FMP_API_KEY                      environment variable — preferred
    2. credentials.local.json           {"api_key": "..."} beside this file,
                                        gitignored, never leaves the machine
    3. hard error naming both

There is deliberately no fourth option that reaches into another project's
config file. A skill that silently reads credentials from wherever it can find
them is one refactor away from reading them from somewhere it should not.
"""

import json
import os
from pathlib import Path

LOCAL = Path(__file__).resolve().parent / "credentials.local.json"

ENV_VAR = "FMP_API_KEY"

_MISSING = f"""No FMP credential found. Set one of:

  1. the {ENV_VAR} environment variable, e.g. in this shell
         export {ENV_VAR}=<key>

  2. {LOCAL.name} beside credentials.py, containing
         {{"api_key": "<key>"}}
     (already in .gitignore — this repo is public, so never commit a key)

A key already exists in solution.atlas at
  config/config.dev.json -> service_providers:fmp:api_key
and can seed either option. Read it from there into the environment rather than
copying it into a file that might be committed."""


def api_key() -> str:
    """The FMP key, or a hard error explaining how to provide one."""
    from_env = os.environ.get(ENV_VAR, "").strip()
    if from_env:
        return from_env

    if LOCAL.exists():
        try:
            key = json.loads(LOCAL.read_text(encoding="utf-8")).get("api_key", "").strip()
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{LOCAL.name} is not valid JSON: {exc}") from exc
        if key:
            return key

    raise SystemExit(_MISSING)
