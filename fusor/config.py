import json
import os

# Path used to store user settings
CONFIG_FILE = os.path.expanduser("~/.fusor_config.json")

# Default configuration values
DEFAULT_CONFIG = {
    "use_docker": False,
    "php_service": "php",
    "server_port": 8000,
    "yii_template": "basic",
    "log_path": os.path.join("storage", "logs", "laravel.log"),
    "projects": [],
    "current_project": "",
    "git_remote": "",
    "compose_files": [],
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
