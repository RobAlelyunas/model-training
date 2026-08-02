import subprocess
import threading
import sys

class ProcessController:
    def __init__(self, target):
        self.target = target
        self.is_callable = callable(target)
        self.process = None
        self.thread = None
        self._cancelled = False
        self._success = None
        self._exit_code = None

    def _run(self):
        try:
            if self.is_callable:
                self.target()
                if self._cancelled:
                    self._success = False
                    self._exit_code = -999
                else:
                    self._success = True
                    self._exit_code = 0
            else:
                self.process = subprocess.Popen(
                    self.target,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    text=True,
                    shell=True,
                )
                self.process.wait()
                self._exit_code = self.process.returncode
                self._success = (self._exit_code == 0 and not self._cancelled)

        except Exception as e:
            print(f"\n[ProcessController] Exception encountered: {e}")
            self._success = False
            self._exit_code = 1

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        return self

    def cancel(self):
        self._cancelled = True
        self._success = False
        if not self.is_callable and self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        print("\n[ProcessController] Terminated by user command.")

    def is_alive(self):
        if self.is_callable:
            return self.thread is not None and self.thread.is_alive()
        else:
            return (
                self.thread is not None 
                and self.thread.is_alive() 
                and (self.process is None or self.process.poll() is None)
            )

    def was_successful(self):
        if self.is_alive():
            return False
        return self._success is True