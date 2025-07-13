import json
import os

# Path used to store user settings
CONFIG_FILE = os.path.expanduser("~/.fusor_config.json")

def load_config():
    """Return configuration values from disk if available.

    Returns
    -------
    dict
        Previously saved configuration values or an empty dict.
    """
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Failed to load config: invalid JSON")
        return {}

def save_config(data):
    """Persist configuration dictionary to disk.

    Parameters
    ----------
    data : dict
        Mapping of configuration keys to persist.
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
