import json
import os

# Path used to store user settings
CONFIG_FILE = os.path.expanduser("~/.fusor_config.json")

def load_config():
    """Return configuration values from disk if available."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"use_docker": False, "php_service": "php", "server_port": 8000}
        data.setdefault("use_docker", False)
        data.setdefault("php_service", "php")
        data.setdefault("server_port", 8000)
        return data
    except FileNotFoundError:
        return {"use_docker": False, "php_service": "php", "server_port": 8000}
    except json.JSONDecodeError:
        print("Failed to load config: invalid JSON")
        return {"use_docker": False, "php_service": "php", "server_port": 8000}

def save_config(data):
    """Persist configuration dictionary to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
