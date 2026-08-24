from src.core.storage import get_properties_path
from src.core.logging import log
import json
import sys


_state = {}
_state_change_handlers = []

def initialize_state():
    global _state
    # 1. read global state from the properties.json file first
    CONFIG_PATH = get_properties_path()
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Properties file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _state = json.load(f)

    # 2. parse any command line arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--"): # Look for flags starting with '--'
            key = arg[2:] # Strip the leading '--' 
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1] # value is the next argument
                _state[key] = value
                i += 2 # Skip both the key and the value for next
            else:
                _state[key] = True #no value so its a boolean flag
                i += 1
        else:
            i += 1

    log("Global State", f"Initialized with properties: {_state}")

def save_state_to_file():
    """Writes the current global state dictionary back out to properties.json."""
    global _state
    try:
        with open(get_properties_path(), "w", encoding="utf-8") as f:
            json.dump(_state, f, indent=4)
    except Exception as e:
        log("State Error",f"Failed to write state to properties.json: {e}")

def register_state_change_handler(handler):
    """Registers a parameterless callback function to be called on global state changes."""
    global _state_change_handlers
    if handler not in _state_change_handlers:
        _state_change_handlers.append(handler)

def get_property(key: str):
    """Strict property getter: raises a KeyError if the property is missing."""
    global _state
    if key not in _state:
        raise KeyError(f"[Error] Mandatory property '{key}' is not found, check your configuration")
    return _state[key]

def set_property(key: str, value):
    """Dynamically set or override a property value at runtime and persist it to disk."""
    global _state
    _state[key] = value
    log("Set Property", f"Property '{key}' set to: {value}")
    save_state_to_file()   
    notify_global_state_change()

def notify_global_state_change():
    """Whenever the global state changes, this method notifies all registered handlers."""
    global _state_change_handlers
    for handler in _state_change_handlers:
        try:
            handler()
        except Exception as e:
            log("State Error", f"Error executing state change handler: {e}")