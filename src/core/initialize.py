import sys
from pathlib import Path

_INITIALIZED = False

def init():
    """Initializes the application, running only once."""
    global _INITIALIZED
    if _INITIALIZED:
        return
        
    from src.core.storage import initialize_app_storage
    initialize_app_storage()

    from src.core.global_state import initialize_state      
    initialize_state()

    setup_logging()

    _INITIALIZED = True

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