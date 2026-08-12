import threading

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