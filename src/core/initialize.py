import subprocess
import sys
import platform
from pathlib import Path


_INITIALIZED = False

def init():
    """Initializes the application, running only once."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    total_memory_gb = check_hardware()
    print(f"[Bootstrap] Apple Silicon with total memory {total_memory_gb}")

    from src.core.storage import initialize_app_storage, get_properties_dir
    
    # A fresh install won't have the properties file yet
    config_path = get_properties_dir() / "properties.json"
    first_run = not config_path.exists()
    
    print(f"[Bootstrap] First run: {first_run}")

    # Initialize storage, passing the first_run flag
    initialize_app_storage(first_run=first_run)

    from src.core.global_state import initialize_state      
    initialize_state()

    setup_logging()

    from src.core.global_state import set_property 
    set_property("total_memory_gb", total_memory_gb)

    _INITIALIZED = True

def abort_due_to_incompatible_hardware(msg):
    # This runs before there is a UI, so set up a quick UI
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title="Incompatible Hardware",
                        message=msg,
                        parent=root)
    root.destroy()
    sys.exit(1)

def check_hardware():
    if sys.platform != "darwin":
        abort_due_to_incompatible_hardware("This software can only run on MacOs, Exiting ...")
    if platform.machine() != "arm64":
        abort_due_to_incompatible_hardware(f"Apple Silicon processor required (for native model training support), your processor type is {platform.machine()}, Exiting ...")
    result = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, check=True)
    total_memory_bytes = int(result.stdout.strip()) 
    total_memory_gb = round(total_memory_bytes / (1024 ** 3), 1)
    return total_memory_gb

def setup_logging():
    """
    Redirects stdout and stderr to a log file if running as a frozen app bundle,
    ensuring crashes and print statements aren't lost to the void.
    """
    # Only force-redirect if we are running as a packaged .app bundle 
    # (keeps normal terminal output active during local development)
    if getattr(sys, 'frozen', False):
        from src.core.storage import get_logs_dir
        log_dir = get_logs_dir()
        
        log_file_path = log_dir / "app_output.log"
        
        # Open the log file in append mode and override stdout/stderr
        log_file = open(log_file_path, "w", encoding="utf-8")
        sys.stdout = log_file
        sys.stderr = log_file
        
        print(f"--- Application Started: {Path(__file__).name} ---")