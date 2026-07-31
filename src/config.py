import json
from pathlib import Path

CONFIG_PATH = Path("resources") / "properties.json"

def _load_properties():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(f"Properties file not found at: {CONFIG_PATH}")

_properties = _load_properties()

def get_property(key: str):
    """Strict property getter: raises a KeyError if the property is missing."""
    if key not in _properties:
        raise KeyError(f"[Configuration Error] Mandatory property '{key}' is missing from {CONFIG_PATH}!")
    return _properties[key]
