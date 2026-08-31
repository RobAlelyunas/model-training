import functools
import threading
from tkinter import messagebox
from src.core.global_state import get_property
from src.core.logging import log

def run_background(widget_context, task_func, ui_callback=None):
    """Runs a function in a background thread, using a Tkinter widget context
    to safely schedule the completion callback back on the main thread via .after().
    """
    def worker():
        try:
            result = task_func()
            if ui_callback is None:
                return

            callback = ui_callback
            if result is not None:
                widget_context.after(0, lambda: callback(result))
            else:
                widget_context.after(0, callback)
        except Exception as e:
            log("Background Task Error", f"{e}")

    threading.Thread(target=worker, daemon=True).start()

def requires(*properties):
    """Decorator that guards a method by checking for specified properties"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for prop in properties:
                val = get_property(prop)
                if not val.strip():
                    if prop == "target_model":
                        msg = "A target model is needed for this action.\n\nPlease go to the setup screen and choose a target model."
                    elif prop == "source_model":
                        msg = "A source model is needed for this action.\n\nPlease go to the setup screen and choose a source model."
                    elif prop == "dataset":
                        msg = "A dataset is required for this action.\n\nPlease go to the setup screen and select a dataset."
                    elif prop == "chat_model":
                        msg = "A chat model is required for this action.\n\nPlease go to the setup screen and select a dataset."
                    else:
                        msg = f"The '{prop}' property must be set before proceeding."
                    messagebox.showinfo("Prerequisite Required", msg, parent=self)
                    return  # Do not execute the action
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

