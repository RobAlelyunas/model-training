import json
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from src.core.global_state import get_property, register_state_change_handler
from src.core.storage import get_datasets_dir
from src.ui.ui_helpers import requires
from src.ui.ui_theme import create_styled_text

class DataTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.dataset = get_property("dataset")
        self.file_version = get_property("dataset_version")
        self.current_index = 0
        self.is_dirty = False
        self.create_widgets()
        self.load_current_record()
        self.prompt_text.bind("<<Modified>>", self.on_widget_modified)
        self.completion_text.bind("<<Modified>>", self.on_widget_modified)
        register_state_change_handler(self.global_state_changed)

    def global_state_changed(self):
        new_file_version = get_property("dataset_version")
        new_dataset = get_property("dataset")
        if new_dataset != self.dataset:
            # dataset changed: switch file, reset index to 0, and load[cite: 8]
            self.dataset = new_dataset
            self.file_version = new_file_version
            self.current_index = 0
            self.load_current_record()
        elif new_file_version != self.file_version:
            # File version changed externally: update version tracker and reload current record[cite: 8]
            self.file_version = new_file_version
            self.load_current_record()

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=15, pady=15)

        # Navigation and Record count frame
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill="x", padx=15, pady=5)

        self.prev_button = ttk.Button(nav_frame, text="◀ Previous", command=self.prev_record)
        self.prev_button.pack(side="left", padx=5)

        self.next_button = ttk.Button(nav_frame, text="Next ▶", command=self.next_record)
        self.next_button.pack(side="left", padx=5)

        self.index_label = ttk.Label(nav_frame, text="Record: 1 / 1")
        self.index_label.pack(side="left", padx=10)

        # Smooth Record Slider for quick navigation
        self.slider_var = tk.IntVar(value=1)
        self.record_slider = ttk.Scale(
            nav_frame, 
            from_=1, 
            to=1, 
            orient="horizontal", 
            variable=self.slider_var,
            command=self.on_slider_motion
        )
        self.record_slider.pack(side="left", fill="x", expand=True, padx=15)
        self.record_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.new_button = ttk.Button(nav_frame, text="+ Add New Record", command=self.add_record)
        self.new_button.pack(side="right", padx=5)

        self.delete_button = ttk.Button(nav_frame, text="Delete Record", command=self.delete_record)
        self.delete_button.pack(side="right", padx=5)

        # Main editor container
        editor_container = ttk.Frame(self)
        editor_container.pack(expand=True, fill="both", padx=15, pady=10)
        editor_container.rowconfigure(0, weight=1)
        editor_container.rowconfigure(1, weight=1)
        editor_container.columnconfigure(0, weight=1)

        # Prompt Section
        prompt_frame = ttk.LabelFrame(editor_container, text="Prompt (Input)")
        prompt_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        prompt_frame.rowconfigure(0, weight=1)
        prompt_frame.columnconfigure(0, weight=1)

        self.prompt_text = create_styled_text(prompt_frame, height=10)
        self.prompt_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=0, column=1, sticky="ns", pady=5)
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)

        # Completion Section
        completion_frame = ttk.LabelFrame(editor_container, text="Completion (Target Response)")
        completion_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        completion_frame.rowconfigure(0, weight=1)
        completion_frame.columnconfigure(0, weight=1)

        self.completion_text = create_styled_text(completion_frame, height=10)
        self.completion_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        completion_scroll = ttk.Scrollbar(completion_frame, orient="vertical", command=self.completion_text.yview)
        completion_scroll.grid(row=0, column=1, sticky="ns", pady=5)
        self.completion_text.configure(yscrollcommand=completion_scroll.set)

    def on_widget_modified(self, event=None):
        for w in (self.prompt_text, self.completion_text):
            if w.edit_modified():
                w.edit_modified(False)
        self.is_dirty = True

    def _get_total_line_count(self) -> int:
        if not self.dataset:
            return 0
        count = 0
        data_path = get_datasets_dir() / self.dataset
        if not data_path.exists():
            return 0
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def _read_line_from_file(self, index: int) -> dict:
        if not self.dataset:
            return {"prompt": "", "completion": ""}
        
        current_idx = 0
        data_path = get_datasets_dir() / self.dataset
        if not data_path.exists():
            return {"prompt": "", "completion": ""}

        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    if current_idx == index:
                        try:
                            data = json.loads(line)
                            return {
                                "prompt": data.get("prompt", ""),
                                "completion": data.get("completion", "")
                            }
                        except Exception:
                            break
                    current_idx += 1
        return {"prompt": "", "completion": ""}

    def load_current_record(self):
        total = self._get_total_line_count()
        if total == 0:
            total = 1
            if self.current_index >= total:
                self.current_index = 0

        if self.current_index >= total:
            self.current_index = total - 1

        record = self._read_line_from_file(self.current_index)

        self.prompt_text.delete("1.0", "end")
        self.completion_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", record.get("prompt", ""))
        self.completion_text.insert("1.0", record.get("completion", ""))

        self.is_dirty = False

        self.index_label.config(text=f"Record: {self.current_index + 1} / {total}")
        
        # Update slider configuration safely without triggering unwanted slider events
        self.record_slider.config(to=total)
        self.slider_var.set(self.current_index + 1)

    def on_slider_motion(self, event=None):
        """Updates the label dynamically as the user drags the slider."""
        target_val = int(self.slider_var.get())
        total = self._get_total_line_count() or 1
        self.index_label.config(text=f"Record: {target_val} / {total}")

    def on_slider_release(self, event=None):
        """Saves current state and jumps to the selected slider record position upon release."""
        target_index = int(self.slider_var.get()) - 1
        total = self._get_total_line_count()
        if total > 0:
            target_index = max(0, min(target_index, total - 1))
            if target_index != self.current_index:
                if self.save_current_record():
                    self.current_index = target_index
                    self.load_current_record()

    def save_current_record(self) -> bool:
        """Saves the active record to disk only if modifications were made[cite: 8]."""
        if not self.is_dirty:
            return True

        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        completion = self.completion_text.get("1.0", "end-1c").strip()
        new_line_str = json.dumps({"prompt": prompt, "completion": completion}, ensure_ascii=False) + "\n"

        try:
            lines = []
            if self.dataset:
                data_path = get_datasets_dir() / self.dataset
                if data_path.exists():
                    with open(data_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

            while len(lines) <= self.current_index:
                lines.append("\n")

            lines[self.current_index] = new_line_str

            with open(data_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            self.is_dirty = False
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save record:\n{e}")
            return False

    @requires("dataset")
    def next_record(self):
        if self.save_current_record():
            total = self._get_total_line_count()
            if self.current_index < total - 1:
                self.current_index += 1
                self.load_current_record()

    @requires("dataset")
    def prev_record(self):
        if self.save_current_record():
            if self.current_index > 0:
                self.current_index -= 1
                self.load_current_record()

    @requires("dataset")
    def add_record(self):
        if self.save_current_record():
            blank_line = json.dumps({"prompt": "", "completion": ""}, ensure_ascii=False) + "\n"
            data_path = get_datasets_dir() / self.dataset
            try:
                with open(data_path, "a", encoding="utf-8") as f:
                    f.write(blank_line)
                
                self.current_index = self._get_total_line_count() - 1
                self.load_current_record()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add record:\n{e}")

    @requires("dataset")
    def delete_record(self):
        try:
            lines = []
            if self.dataset:
                data_path = get_datasets_dir() / self.dataset
                if data_path.exists():
                    with open(data_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

            if len(lines) <= 1:
                self.prompt_text.delete("1.0", "end")
                self.completion_text.delete("1.0", "end")
                self.is_dirty = True
                self.save_current_record()
                return

            if 0 <= self.current_index < len(lines):
                lines.pop(self.current_index)

            with open(data_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            if self.current_index >= len(lines):
                self.current_index = max(0, len(lines) - 1)

            self.load_current_record()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record:\n{e}")