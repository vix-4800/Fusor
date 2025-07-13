import json
import os

# Path used to store user settings
CONFIG_FILE = os.path.expanduser("~/.fusor_config.json")

def load_config():
    """Return configuration values from disk if available."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Failed to load config: invalid JSON")
        return {}

def save_config(data):
    """Persist configuration dictionary to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
