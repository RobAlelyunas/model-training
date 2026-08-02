import json
import sys
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

def set_property(key: str, value):
    """Dynamically set or override a property value at runtime."""
    _properties[key] = value
    print(f"[Configuration Override] Property '{key}' set to: {value}")

def load_command_line_overrides():
    """
    Dynamically scans sys.argv for any key-value pairs starting with '--' 
    and overrides or adds them directly to the properties dictionary.
    """
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        # Look for flags starting with '--'
        print(f"[Command Line Override] Processing argument: {arg}")
        if arg.startswith("--"):
            key = arg[2:] # Strip the leading '--'
            
            # Check if there is a corresponding value next
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                set_property(key, value)
                i += 2 # Skip both the key and the value
            else:
                # Flag passed without an explicit value (treat as True flag)
                set_property(key, True)
                i += 1
        else:
            i += 1