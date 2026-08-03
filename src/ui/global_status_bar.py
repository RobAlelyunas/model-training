import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
from src.global_state import get_property, set_property
from src.services.inference_engine import inference_engine


class GlobalStatusBar(ttk.Frame):
    """A persistent toolbar widget that manages global application context:
    Source Model, Target Model, and Active Dataset drop-downs distributed evenly across available space.
    """
    def __init__(self, parent):
        super().__init__(parent, relief="groove", borderwidth=1)
        
        self.source_mapping = {}
        self.target_mapping = {}
        self.dataset_mapping = {}

        self.create_widgets()
        self.refresh()

    def notify_global_state_change(self):
        """Refreshes the drop-downs to reflect any changes in global state."""
        self.refresh()
        
    def create_widgets(self):
        # Configure a 3-column grid layout where each column expands evenly to fill the width
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # 1. Source Model Section
        source_frame = ttk.Frame(self)
        source_frame.grid(row=0, column=0, padx=5, pady=6, sticky="ew")
        source_frame.columnconfigure(1, weight=1)

        ttk.Label(source_frame, text="Source:", font=("Helvetica", 9, "bold")).grid(row=0, column=0, padx=(5, 4), sticky="w")
        self.source_var = tk.StringVar()
        self.source_dropdown = ttk.OptionMenu(
            source_frame, self.source_var, "", command=self.on_source_changed
        )
        self.source_dropdown.grid(row=0, column=1, sticky="ew")

        # 2. Target Model Section
        target_frame = ttk.Frame(self)
        target_frame.grid(row=0, column=1, padx=5, pady=6, sticky="ew")
        target_frame.columnconfigure(1, weight=1)

        ttk.Label(target_frame, text="Target:", font=("Helvetica", 9, "bold")).grid(row=0, column=0, padx=(5, 4), sticky="w")
        self.target_var = tk.StringVar()
        self.target_dropdown = ttk.OptionMenu(
            target_frame, self.target_var, "", command=self.on_target_changed
        )
        self.target_dropdown.grid(row=0, column=1, sticky="ew")

        # 3. Dataset File Section
        dataset_frame = ttk.Frame(self)
        dataset_frame.grid(row=0, column=2, padx=5, pady=6, sticky="ew")
        dataset_frame.columnconfigure(1, weight=1)

        ttk.Label(dataset_frame, text="Dataset:", font=("Helvetica", 9, "bold")).grid(row=0, column=0, padx=(5, 4), sticky="w")
        self.dataset_var = tk.StringVar()
        self.dataset_dropdown = ttk.OptionMenu(
            dataset_frame, self.dataset_var, "", command=self.on_dataset_changed
        )
        self.dataset_dropdown.grid(row=0, column=1, sticky="ew")

    def _update_option_menu(self, menu_widget, var, items, default_val, callback):
        """Helper to clear and rebuild a standard ttk.OptionMenu drop-down safely."""
        menu = menu_widget["menu"]
        menu.delete(0, "end")
        
        if not items:
            var.set("")
            return

        if default_val in items:
            var.set(default_val)
        else:
            var.set(items[0])
            callback(items[0])

        for item in items:
            menu.add_command(label=item, command=lambda val=item: (var.set(val), callback(val)))

    def refresh(self):
        """Scans local file system directories to populate all three drop-downs."""
        # --- Populate Sources ---
        self.source_mapping.clear()
        source_dir = Path("models/sources")
        source_items = []
        if source_dir.exists() and source_dir.is_dir():
            for child in sorted(source_dir.iterdir()):
                if child.is_dir():
                    source_items.append(child.name)
                    self.source_mapping[child.name] = child.name

        current_source = get_property("source_model")
        self._update_option_menu(
            self.source_dropdown, self.source_var, source_items, current_source, self.on_source_changed
        )

        # --- Populate Targets ---
        self.target_mapping.clear()
        target_dir = Path("models/targets")
        target_items = []
        if target_dir.exists() and target_dir.is_dir():
            for child in sorted(target_dir.iterdir()):
                if child.is_dir():
                    target_items.append(child.name)
                    self.target_mapping[child.name] = child.name

        current_target = get_property("target_model")
        self._update_option_menu(
            self.target_dropdown, self.target_var, target_items, current_target, self.on_target_changed
        )

        # --- Populate Datasets ---
        self.dataset_mapping.clear()
        resources_dir = Path("resources")
        dataset_items = []
        if resources_dir.exists() and resources_dir.is_dir():
            for child in sorted(resources_dir.glob("*.jsonl")):
                if child.is_file():
                    dataset_items.append(child.name)
                    self.dataset_mapping[child.name] = str(child)

        current_dataset_path = get_property("dataset_path")
        current_dataset = Path(current_dataset_path).name if current_dataset_path else ""
        
        def _internal_dataset_callback(val):
            if val in self.dataset_mapping:
                set_property("dataset_path", self.dataset_mapping[val])

        self._update_option_menu(
            self.dataset_dropdown, self.dataset_var, dataset_items, current_dataset, _internal_dataset_callback
        )
        if current_dataset in dataset_items:
            set_property("dataset_path", self.dataset_mapping[current_dataset])
        elif dataset_items:
            set_property("dataset_path", self.dataset_mapping[dataset_items[0]])

    def on_source_changed(self, selected):
        if selected:
            set_property("source_model", selected)

    def on_dataset_changed(self, selected):
        if selected and selected in self.dataset_mapping:
            path_str = self.dataset_mapping[selected]
            set_property("dataset_path", path_str)

    def on_target_changed(self, target_name):
        if target_name:
            set_property("target_model", target_name)
            self.trigger_model_reload(target_name)

    def trigger_model_reload(self, target_name: str):
        def _reload_task():
            try:
                inference_engine.unload_model()
                inference_engine.load_model()
            except Exception:
                pass

        threading.Thread(target=_reload_task, daemon=True).start()