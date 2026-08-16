import threading
from src.core.global_state import get_property

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
            print(f"[Background Task Error] {e}")

    threading.Thread(target=worker, daemon=True).start()


def ensure_setup_complete() -> bool:
    """
    Checks if all mandatory setup items are configured.
    """
    source_model = get_property("source_model")
    target_model = get_property("target_model")
    dataset = get_property("dataset")
    chat_template = get_property("chat_template")
    
    # Check if all required properties are present and non-empty
    return source_model and target_model and dataset and chat_template
