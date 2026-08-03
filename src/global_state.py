import json
import sys
from pathlib import Path

CONFIG_PATH = Path("resources") / "properties.json"

_state = {}
_state_change_handlers = []

def _init_state():
    global _state
    # 1. read global state from the properties.json file first
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _state = json.load(f)

    # parse any command line arguments
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

    # 3. set additional global state as needed
    _state["dataset_version"] = 0

_init_state()

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
    """Dynamically set or override a property value at runtime."""
    global _state
    _state[key] = value
    print(f"[Set Property] Property '{key}' set to: {value}")
    notify_global_state_change()

def notify_global_state_change():
    """Whenever the global state changes, this method notifies all registered handlers."""
    global _state_change_handlers
    for handler in _state_change_handlers:
        try:
            handler()
        except Exception as e:
            print(f"[State Error] Error executing state change handler: {e}")


