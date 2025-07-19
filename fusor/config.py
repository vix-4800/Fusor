import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Path used to store user settings
CONFIG_FILE = Path.home() / ".fusor_config.json"

# Default maximum number of log lines stored per project
DEFAULT_MAX_LOG_LINES = 1000

# Default per-project settings
DEFAULT_PROJECT_SETTINGS = {
    "framework": "Laravel",
    "php_path": "php",
    "php_service": "php",
    "server_port": 8000,
    "use_docker": False,
    "yii_template": "basic",
    # list of log files for the project
    "log_paths": [],
    "git_remote": "",
    "compose_files": [],
    "compose_profile": "",
    "auto_refresh_secs": 5,
    "max_log_lines": DEFAULT_MAX_LOG_LINES,
}

# Default configuration values
# ``projects`` previously stored a list of paths.  To allow storing extra
# information per project (like a display name) it now stores a list of
# dictionaries with at least ``path`` and ``name`` keys.
DEFAULT_CONFIG = {
    "projects": [],  # list[dict]
    "current_project": "",
    "project_settings": {},
    "theme": "dark",
    # Window geometry (width, height) and position (x, y)
    "window_size": [1024, 768],
    "window_position": [100, 100],
}


def load_config():
    """Return configuration values from disk if available."""
    try:
        config_path = Path(CONFIG_FILE)
        with config_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return DEFAULT_CONFIG.copy()
        for key, value in DEFAULT_CONFIG.items():
            data.setdefault(key, value)

        # migrate list of project paths into list of dicts
        projects = []
        for entry in data.get("projects", []):
            if isinstance(entry, str):
                projects.append({"path": entry, "name": Path(entry).name})
            elif isinstance(entry, dict) and "path" in entry:
                proj = {
                    "path": entry["path"],
                    "name": entry.get("name", Path(entry["path"]).name),
                }
                for k, v in entry.items():
                    if k not in proj:
                        proj[k] = v
                projects.append(proj)
        data["projects"] = projects

        # migrate old flat settings into per-project block
        current = data.get("current_project") or data.get("project_path")
        if current:
            settings = data.setdefault("project_settings", {}).setdefault(current, {})
            for k in DEFAULT_PROJECT_SETTINGS:
                if k in data and k not in settings:
                    settings[k] = data[k]
            if "log_path" in data and "log_paths" not in settings:
                settings["log_paths"] = [data["log_path"]]

        if "project_path" in data and data["project_path"]:
            path = data["project_path"]
            if not any(p.get("path") == path for p in data["projects"]):
                data["projects"].append({"path": path, "name": Path(path).name})
            if not data["current_project"]:
                data["current_project"] = path

        return data
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        logger.warning("Failed to load config: invalid JSON")
        return DEFAULT_CONFIG.copy()


def save_config(data):
    """Persist configuration dictionary to disk."""
    config_path = Path(CONFIG_FILE)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
