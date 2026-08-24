
import datetime
import sys

_LOG_FILE = None

def initialize_logging():
    from src.core.storage import get_logs_dir
    log_dir = get_logs_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = log_dir / f"app_output_{timestamp}.txt"
    _LOG_FILE = open(log_file_path, "w", encoding="utf-8", buffering=1)
    sys.stdout = _LOG_FILE
    sys.stderr = _LOG_FILE

def log(module="", msg=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # logging is best sent to STDOUT, not written directly to files,
    #  because the context of the caller should determine where process output goes. 
    print(f"{timestamp} [{module}] {msg}")