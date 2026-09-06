import json
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from src.core.global_state import get_property, set_property
from src.core.logging import log
from src.core.storage import get_datasets_dir


class DatasetPanel(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="3. Dataset", padding=15)

        # 1. Dropdown
        self.dataset_var = tk.StringVar()
        self.dataset_combo = ttk.Combobox(
            self, textvariable=self.dataset_var, state="readonly"
        )
        self.dataset_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.dataset_combo.bind("<<ComboboxSelected>>", self.on_dataset_selected)
        self.dataset_combo.bind("<Button-1>", lambda e: self.load_datasets())

        # 2. Directory Path Box
        self.dataset_path_str = str(get_datasets_dir())
        self.dataset_path_text = tk.Text(
            self, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1
        )
        self.dataset_path_text.insert("1.0", self.dataset_path_str)
        self.dataset_path_text.configure(state="disabled", bg="#f0f0f0")
        self.dataset_path_text.pack(fill="x", pady=(0, 0))

        # 3. Open Directory Link
        ds_links_frame = ttk.Frame(self)
        ds_links_frame.pack(fill="x", anchor="w", pady=(0, 0))
        link_ds_open = ttk.Label(
            ds_links_frame, text="[open directory]", foreground="blue", cursor="hand2"
        )
        link_ds_open.pack(side="right")
        link_ds_open.bind("<Button-1>", lambda e: self.open_directory(self.dataset_path_str))

        # 4. Create New Dataset Button
        new_dataset_btn = ttk.Button(
            self, text="Create New Dataset", command=self.on_generate_empty_dataset
        )
        new_dataset_btn.pack(side="left")

        self.load_datasets()

    def open_directory(self, path_str):
        subprocess.run(["open", path_str])

    def load_datasets(self):
        try:
            dataset_dir = get_datasets_dir()
            if dataset_dir.exists() and dataset_dir.is_dir():
                files = [item.name for item in dataset_dir.iterdir() if item.is_file()]
                self.dataset_combo["values"] = sorted(files)
            else:
                self.dataset_combo["values"] = []
        except Exception as e:
            log("Setup", f"Error loading datasets: {e}")
            self.dataset_combo["values"] = []

    def on_dataset_selected(self, event):
        val = self.dataset_var.get()
        if val:
            set_property("dataset", val)
            set_property("dataset_version", 0)

    def on_generate_empty_dataset(self):
        dataset_name = simpledialog.askstring(
            "Generate Empty Dataset",
            "Enter a name for the new dataset:",
            initialvalue="new_working_dataset.jsonl",
            parent=self,
        )

        if dataset_name:
            if not dataset_name.endswith(".jsonl"):
                dataset_name += ".jsonl"

            file_path = get_datasets_dir() / dataset_name

            if file_path.exists():
                if not messagebox.askyesno(
                    "File Exists",
                    f"Dataset '{dataset_name}' already exists. Do you want to replace it?",
                    parent=self,
                ):
                    return

            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                initial_record = {"prompt": "Example prompt", "completion": "Example completion"}
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(initial_record) + "\n")

                self.load_datasets()
                self.dataset_var.set(dataset_name)
                set_property("dataset", dataset_name)
                set_property("dataset_version", 0)
                messagebox.showinfo("Success", f"Created new dataset '{dataset_name}'.", parent=self)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create dataset:\n{e}", parent=self)