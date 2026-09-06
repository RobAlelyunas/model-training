import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

from src.core.global_state import get_property, set_property
from src.core.storage import get_source_models_dir
from src.services.training_service import training_service
from src.ui.apply_tab import TaskHandle
from src.ui.ui_helpers import run_background


class SourceModelPanel(ttk.LabelFrame):
    def __init__(self, parent, on_source_changed_callback=None):
        super().__init__(parent, text="1. Source Model", padding=15)
        self.on_source_changed_callback = on_source_changed_callback

        # 1. Dropdown
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(
            self, textvariable=self.source_var, state="readonly"
        )
        self.source_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.source_combo.bind("<<ComboboxSelected>>", self.on_source_selected)
        self.source_combo.bind("<Button-1>", lambda e: self.load_source_models())

        # 2. Directory Path Box
        self.source_path_str = str(get_source_models_dir())
        self.path_text = tk.Text(
            self, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1
        )
        self.path_text.insert("1.0", self.source_path_str)
        self.path_text.configure(state="disabled", bg="#f0f0f0")
        self.path_text.pack(fill="x", pady=(0, 0))

        # 3. Open Directory Link
        src_links_frame = ttk.Frame(self)
        src_links_frame.pack(fill="x", anchor="w", pady=(0, 5))
        link_open = ttk.Label(
            src_links_frame, text="[open directory]", foreground="blue", cursor="hand2"
        )
        link_open.pack(side="right")
        link_open.bind("<Button-1>", lambda e: self.open_directory(self.source_path_str))

        # 4. Download Starter Model Button
        download_starter_btn = ttk.Button(
            self,
            text="Download Starter Model",
            command=self.on_download_starter_model,
        )
        download_starter_btn.pack(side="left")

        self.task_handle = None
        self.load_source_models()

    def open_directory(self, path_str):
        subprocess.run(["open", path_str])

    def load_source_models(self):
        try:
            source_dir = get_source_models_dir()
            if source_dir.exists() and source_dir.is_dir():
                dirs = [item.name for item in source_dir.iterdir() if item.is_dir()]
                self.source_combo["values"] = sorted(dirs)
            else:
                self.source_combo["values"] = []
        except Exception as e:
            self.source_combo["values"] = []

    def on_source_selected(self, event):
        val = self.source_var.get()
        if val:
            set_property("source_model", val)
            if self.on_source_changed_callback:
                self.on_source_changed_callback(val)

    def on_download_starter_model(self):
        repo_id = get_property("starter_model")
        if not repo_id:
            messagebox.showwarning("Missing Property", "No starter_model property configured.", parent=self)
            return

        model_name = repo_id.rsplit("/", 1)[-1] if "/" in repo_id else repo_id
        model_path = get_source_models_dir() / model_name

        if model_path.exists():
            messagebox.showwarning(
                "Starter Model Exists",
                f"The starter model '{model_name}' already exists in the source models directory.\n\n"
                f"Please remove or rename before continuing.",
                parent=self,
            )
            return

        # Simple Modal Window
        modal = tk.Toplevel(self)
        modal.title("Downloading Starter Model")
        modal.geometry("650x220")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        lbl_info = ttk.Label(
            modal,
            text=f"Downloading {repo_id}...",
            font=("Helvetica", 11, "bold"),
        )
        lbl_info.pack(anchor="w", padx=15, pady=(15, 8))

        # Live Terminal/Progress Output Display
        progress_display = tk.Text(
            modal,
            height=5,
            font=("Courier", 11),
            bg="#f8f9fa",
            fg="#212529",
            relief="solid",
            bd=1,
            wrap="none"
        )
        progress_display.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Control Row
        control_frame = ttk.Frame(modal)
        control_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.task_handle = TaskHandle() 

        def on_cancel():
            if self.task_handle:
                self.task_handle.cancel()
                btn_cancel.config(state="disabled")

        btn_cancel = ttk.Button(control_frame, text="Cancel", command=on_cancel)
        btn_cancel.pack(side="right", padx=(5, 0))

        btn_done = ttk.Button(control_frame, text="Done", state="disabled", command=modal.destroy)
        btn_done.pack(side="right")

        # Background Execution via TaskHandle
        def task():
            
            if self.task_handle:
                self.task_handle.set_widget(progress_display)

            training_service.download_source_model(repo_id, self.task_handle)

        def on_complete():
            btn_cancel.config(state="disabled")
            btn_done.config(state="normal")

            if self.task_handle and self.task_handle.is_cancelled():
                messagebox.showwarning("Cancelled", "Download process was stopped.", parent=modal)
            else:
                self.load_source_models()
                self.source_var.set(model_name)
                self.on_source_selected(None)
                messagebox.showinfo(
                    "Download Complete",
                    f"Successfully downloaded {model_name}!",
                    parent=modal,
                )

        run_background(self, task, ui_callback=on_complete)