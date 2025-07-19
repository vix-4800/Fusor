import json
from pathlib import Path
from copy import deepcopy
from typing import Any

# Path used to store user settings
CONFIG_FILE = Path.home() / ".fusor_config.json"

# Default maximum number of log lines stored per project
DEFAULT_MAX_LOG_LINES = 1000

# Default per-project settings
DEFAULT_PROJECT_SETTINGS = {
    "framework": "Laravel",
    "php_path": "php",
    "php_service": "php",
    # path of the project inside docker containers
    "docker_project_path": "/app",
    "server_port": 8000,
    "use_docker": False,
    "yii_template": "basic",
    # list of directories containing log files for the project
    "log_dirs": [],
    "git_remote": "",
    "compose_files": [],
    "compose_profile": "",
    "auto_refresh_secs": 5,
    "open_browser": False,
    "max_log_lines": DEFAULT_MAX_LOG_LINES,
    "enable_terminal": False,
}

# Default configuration values
# ``projects`` stores a list of dictionaries.  Each dictionary includes at
# minimum ``path`` and ``name`` along with per-project settings like
# ``framework`` or ``php_path``.
DEFAULT_CONFIG = {
    "projects": [],  # list[dict]
    "current_project": "",
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
            return deepcopy(DEFAULT_CONFIG)
        for key, value in DEFAULT_CONFIG.items():
            data.setdefault(key, value)

        # normalize project entries to dicts
        projects: list[dict] = []
        for entry in data.get("projects", []):
            if isinstance(entry, str):
                projects.append({"path": entry, "name": Path(entry).name})
            elif isinstance(entry, dict) and "path" in entry:
                proj_dict = {"path": entry["path"], "name": entry.get("name", Path(entry["path"]).name)}
                for k, v in entry.items():
                    if k not in proj_dict:
                        proj_dict[k] = v
                projects.append(proj_dict)
        data["projects"] = projects

        # migrate old flat settings into current project entry
        current = data.get("current_project") or data.get("project_path")
        if current:
            proj: dict[str, Any] | None = next(
                (p for p in data["projects"] if p.get("path") == current),
                None,
            )
            if proj is None:
                proj = {"path": current, "name": Path(current).name}
                data["projects"].append(proj)
            for k in DEFAULT_PROJECT_SETTINGS:
                if k in data and k not in proj:
                    proj[k] = data[k]
            if "log_path" in data and "log_dirs" not in proj:
                proj["log_dirs"] = [data["log_path"]]
            if "log_paths" in proj:
                proj["log_dirs"] = proj.pop("log_paths")

        if "project_path" in data and data["project_path"]:
            path = data["project_path"]
            if not any(p.get("path") == path for p in data["projects"]):
                data["projects"].append({"path": path, "name": Path(path).name})
            if not data.get("current_project"):
                data["current_project"] = path

        return data
    except FileNotFoundError:
        return deepcopy(DEFAULT_CONFIG)
    except json.JSONDecodeError:
        print("Failed to load config: invalid JSON")
        return deepcopy(DEFAULT_CONFIG)


def save_config(data):
    """Persist configuration dictionary to disk."""
    config_path = Path(CONFIG_FILE)
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
