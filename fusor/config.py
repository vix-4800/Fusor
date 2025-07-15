import json
import os

# Path used to store user settings
CONFIG_FILE = os.path.expanduser("~/.fusor_config.json")

# Default per-project settings
DEFAULT_PROJECT_SETTINGS = {
    "framework": "Laravel",
    "php_path": "php",
    "php_service": "php",
    "server_port": 8000,
    "use_docker": False,
    "yii_template": "basic",
    "log_path": os.path.join("storage", "logs", "laravel.log"),
    "git_remote": "",
    "compose_files": [],
    "auto_refresh_secs": 5,
    "max_log_lines": 1000,
}

# Default configuration values
DEFAULT_CONFIG = {
    "projects": [],
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
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return DEFAULT_CONFIG.copy()
        for key, value in DEFAULT_CONFIG.items():
            data.setdefault(key, value)

        # migrate old flat settings into per-project block
        current = data.get("current_project") or data.get("project_path")
        if current:
            settings = data.setdefault("project_settings", {}).setdefault(current, {})
            for k in DEFAULT_PROJECT_SETTINGS:
                if k in data and k not in settings:
                    settings[k] = data[k]

        if "project_path" in data and data["project_path"]:
            if data["project_path"] not in data["projects"]:
                data["projects"].append(data["project_path"])
            if not data["current_project"]:
                data["current_project"] = data["project_path"]

        return data
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        print("Failed to load config: invalid JSON")
        return DEFAULT_CONFIG.copy()

def save_config(data):
    """Persist configuration dictionary to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
