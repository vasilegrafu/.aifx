"""Where this skill sits, and what it can find from there.

ONE ASCENT, ONE MARKER: the `.claude` directory. Everything else is derived
from it, so the things that need a path cannot disagree about the layout.

    <project>/                      PROJECT_ROOT  version, config, secrets, environment
      .claude/                      CLAUDE_DIR
        skills/finance-reports/     SKILL_DIR     this skill

The shape is the same in this repository and in a project the skill is
installed into, which is the whole point: there is no second layout to get
wrong. Counting parents was, and it was wrong in the one place it could not be
tested — the repo it is developed in.

Paths resolve() through junctions, so a skill LINKED into a project reads the
clone it was linked from: one machine, one set of credentials, and nothing
lands in the consuming repository. A skill COPIED in is a real file tree and
needs its own.
"""

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent


def _ascend(start: Path, marker: str) -> Path:
    """Nearest ancestor of `start` containing `marker`. Hard error, no guess."""
    for directory in [start, *start.parents]:
        if (directory / marker).exists():
            return directory
    raise SystemExit(
        f"no {marker!r} directory above {start}.\n"
        f"This skill finds its configuration by locating the .claude directory "
        f"it lives in, so it must be installed as "
        f"<project>/.claude/skills/<name>/ -- copied there, or linked.")


PROJECT_ROOT = _ascend(SKILL_DIR, ".claude")
CLAUDE_DIR = PROJECT_ROOT / ".claude"

#: The version pin every generated page carries -- at the project root, beside
#: the other facts about which checkout this is. A COPIED skill therefore needs
#: one written beside it; if a consuming project already has a version.json of
#: its own, `cdn_href()` rejects it by name for having no "cdn" key rather than
#: pinning every page to a version that means something else.
VERSION_FILE = PROJECT_ROOT / "version.json"

#: Where this skill sits inside the published repo -- the CDN path suffix.
CDN_SUFFIX = SKILL_DIR.relative_to(PROJECT_ROOT).as_posix()
