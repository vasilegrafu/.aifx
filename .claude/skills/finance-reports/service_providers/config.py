"""Non-secret settings for the service providers — the twin of credentials.py.

    <project>/config.<env>.json     TRACKED     api_url, anything not secret
    <project>/secrets.<env>.json    GITIGNORED  api_key, and nothing else

TWO FILES, AND THE SPLIT IS PER-FILE RATHER THAN PER-FIELD. This repository is
public and served by jsDelivr, so "is this safe to commit?" has to be a
property of the FILE, decided once, rather than a judgement made every time
someone adds a field. An `api_key` in a tracked config is not a mistake anyone
makes deliberately — it is one they make by adding a field beside the fields
already there, which is why service_provider() refuses it outright.

Both files are chosen by the SAME environment, so a run cannot read dev config
against a prod key. There is no default; see credentials.resolve().
"""

import json
from pathlib import Path

from _paths import PROJECT_ROOT

from .fmp.credentials import environment


def config_file(env: str | None = None) -> Path:
    """Path to the config file for `env` (default: the selected one)."""
    return PROJECT_ROOT / f"config.{env or environment()}.json"


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
