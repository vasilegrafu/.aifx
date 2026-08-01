"""Non-secret settings for the service providers — the twin of credentials.py.

TWO FILES, AND THE SPLIT IS THE POINT. `config/config.<env>.json` is TRACKED
and holds everything that is merely configuration; `secrets.<env>.json` is
gitignored and holds only what must never be published. This repository is
public and served by jsDelivr, so "is this safe to commit?" has to be a
property of the FILE, decided once, rather than a judgement made per field
every time someone adds one. An `api_key` in a tracked config is not a mistake
anyone makes deliberately — it is one they make by adding a field next to the
fields already there.

Both files are chosen by the SAME environment, so a run cannot read dev config
against a prod key. See credentials.environment(); there is no default, and a
run must say which environment it is.

    config/config.dev.json      api_url, and whatever else is not a secret
    config/config.prod.json     same shape, free to diverge
    secrets.<env>.json          api_key, gitignored

AT THE REPO ROOT, like version.json. The skill already resolves REPO_ROOT to
read the version it pins its assets to, so this is the same dependency the
tree already has, not a new one.
"""

import json
from pathlib import Path

from .fmp.credentials import environment

#: skills/<name>/service_providers/config.py -> the repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = REPO_ROOT / "config"


def config_file(env: str | None = None) -> Path:
    """Path to the config file for `env` (default: the selected one)."""
    return CONFIG_DIR / f"config.{env or environment()}.json"


def load(env: str | None = None) -> dict:
    """The whole config document, or a hard error naming the file.

    Raises rather than returning {}: every caller here needs a real value, and
    a config that silently reads as empty produces a client pointed at nothing
    and a failure reported from three layers away."""
    path = config_file(env)
    if not path.exists():
        raise SystemExit(
            f"missing {path}. Every environment needs a config file; it is "
            f"tracked (no secrets live in it) so it should be in the repo.")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path.name} is not valid JSON: {exc}") from exc


def service_provider(name: str, env: str | None = None) -> dict:
    """One provider's settings, e.g. service_provider("fmp")["api_url"].

    A missing provider or a stray `api_key` are both hard errors. The second
    matters more than it looks: a key that reaches this file is a key in a
    tracked file in a public repo, and the moment to say so is the first build
    after someone pastes it there — not whenever it is next noticed."""
    path = config_file(env)
    providers = load(env).get("service_providers") or {}
    if name not in providers:
        known = ", ".join(sorted(providers)) or "none"
        raise SystemExit(
            f"{path.name} has no service_providers.{name} (known: {known}).")

    settings = providers[name]
    if "api_key" in settings:
        raise SystemExit(
            f"{path.name} carries service_providers.{name}.api_key. This file "
            f"is TRACKED and this repository is PUBLIC — remove it and put the "
            f"key in secrets.{env or environment()}.json instead.")
    return settings
