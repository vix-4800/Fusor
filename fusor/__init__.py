import subprocess

APP_NAME = "Fusor"


def _get_latest_tag(default: str = "0.1.0") -> str:
    """Return the most recent git tag or ``default`` if tags are unavailable."""
    try:
        tag = (
            subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.STDOUT,
            )
            .decode()
            .strip()
        )
        return tag
    except Exception:
        return default


__version__ = _get_latest_tag()

DESCRIPTION = (
    "A minimal PyQt6 application with helper tools for PHP development."
)
AUTHOR = "Anton Vix"

