import atexit
import subprocess
import sys
import threading
from src.core.logging import log

class TaskHandle:
    """Handle for cancelling tasks and splitting output to a Tkinter widget."""
    def __init__(self):
        self._cancelled = False
        self.widget = None
    def cancel(self):
        self._cancelled = True
    def is_cancelled(self):
        return self._cancelled
    def set_widget(self, widget):
        self.widget = widget
    def _write(self, text, tag=None):
        if self.widget and hasattr(self.widget, "winfo_exists") and self.widget.winfo_exists():
            try:
                #self.widget.configure(state="normal")
                self.widget.insert("end", text, tag)
                self.widget.see("end")
                #self.widget.configure(state="disabled")
            except Exception:
                pass  # Handle any race conditions gracefully if destroyed mid-write
    def write(self, text, tag=None):
        if self.widget:
            self.widget.after(0, lambda t=text, tg=tag: self._write(t, tg))

_active_processes = set()

def cleanup_orphan_processes():  
    for process in list(_active_processes):
        if process.poll() is None: # still running
            log("RunCommand", f"Cleaning up orphan process {process} on app exit...")
            _terminate(process)
    _active_processes.clear()

atexit.register(cleanup_orphan_processes)

def _terminate(process: subprocess.Popen, task_handle: TaskHandle | None = None):
    """Sends SIGTERM, waits 1s for natural exit, and kills if still alive."""
    if process.poll() is not None:
        return  # Process is already dead, nothing to terminate

    log("RunCommand", "Sending SIGTERM to process...", task_handle)
    process.terminate()

    # 1. Wait up to 1 second for graceful exit and output flushing
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        pass

    # 2. Force kill if still running after 1 second
    if process.poll() is None:
        log("RunCommand", "Process did not exit after 1s; issuing SIGKILL.", task_handle)
        process.kill()
        process.wait()


def run_cmd(cmd_args: list[str], task_handle: TaskHandle | None = None):
    """Runs a python module in an external UNIX process, making it killable with SIGTERM"""
    is_pyinstllaer_bundle = getattr(sys, "frozen", False)
    
    if is_pyinstllaer_bundle:
        full_cmd = [sys.executable] + cmd_args
    else:
        full_cmd = [sys.executable, "-m", "src.main"] + cmd_args

    log("RunCommand", f"Running command: {' '.join(full_cmd)}", task_handle)

    process = subprocess.Popen(
        full_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=False,
        bufsize=0
    )

    _active_processes.add(process)

    def stdout_reader():
        try:
            if process.stdout:
                while True:
                    char = process.stdout.read(1)
                    if not char:
                        break
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    if task_handle:
                        task_handle.write(char)
        except Exception:
            pass  # Triggers when stdout is forcefully closed

    reader_thread = threading.Thread(target=stdout_reader, daemon=True)
    reader_thread.start()

    # Main control loop: poll cancellation every 100ms while process is alive
    while process.poll() is None:
        if task_handle and task_handle.is_cancelled():
            log("RunCommand", "Cancel requested, terminating process...", task_handle)
            _terminate(process, task_handle)
            break
        threading.Event().wait(0.1)

    # close stdout to ensure reader_thread joins
    if process.stdout:
        try:
            process.stdout.close()
        except Exception:
            pass

    reader_thread.join()

    _active_processes.discard(process)

    if process.returncode != 0 and not (task_handle and task_handle.is_cancelled()):
        raise RuntimeError(f"Command failed with exit code {process.returncode}: {' '.join(full_cmd)}")
