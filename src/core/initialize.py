import subprocess
import sys
import platform
from pathlib import Path

def init():
    """Initializes the application, import and run this before doing any other imports"""

    from src.core.logging import initialize_logging, log
    initialize_logging()
    log("Bootstrap", f"--- Application Started: {Path(__file__).name}) ---")
    
    total_memory_gb = check_hardware()
    log("Bootstrap", f"Apple Silicon with total memory {total_memory_gb}")

    # to force a first run, delete the properties file
    from src.core.storage import get_properties_path
    first_run = not get_properties_path().exists()
    
    log("Bootstrap",f"First run: {first_run}")

    from src.core.storage import initialize_app_storage 
    initialize_app_storage(first_run=first_run)

    from src.core.global_state import initialize_state      
    initialize_state()

    from src.core.global_state import set_property 
    set_property("total_memory_gb", total_memory_gb)

def abort_due_to_incompatible_hardware(msg):
    # This runs before there is a UI, so set up a quick UI for the messagebox
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title="Incompatible Hardware", message=msg, parent=root)
    root.destroy()
    sys.exit(1)

def _is_macos() -> bool:
    return sys.platform.lower() == "darwin"

def check_hardware():
    if not _is_macos():
        abort_due_to_incompatible_hardware("This software can only run on MacOs, Exiting ...")
    if platform.machine() != "arm64":
        abort_due_to_incompatible_hardware(f"Apple Silicon processor required (for native model training support), your processor type is {platform.machine()}, Exiting ...")
    result = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, check=True)
    total_memory_bytes = int(result.stdout.strip()) 
    total_memory_gb = round(total_memory_bytes / (1024 ** 3), 1)
    return total_memory_gb
