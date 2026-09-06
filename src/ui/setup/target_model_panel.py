import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from src.core.global_state import get_property, set_property
from src.core.logging import log
from src.core.storage import get_source_models_dir, get_target_models_dir, get_templates_dir


class TargetModelPanel(ttk.LabelFrame):
    def __init__(self, parent, get_current_source_func=None):
        super().__init__(parent, text="2. Target Model", padding=15)
        self.get_current_source_func = get_current_source_func

        # 1. Dropdown
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(
            self, textvariable=self.target_var, state="readonly"
        )
        self.target_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_selected)
        self.target_combo.bind("<Button-1>", lambda e: self.load_target_models())

        # 2. Directory Path Box
        self.target_path_str = str(get_target_models_dir())
        self.target_path_text = tk.Text(
            self, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1
        )
        self.target_path_text.insert("1.0", self.target_path_str)
        self.target_path_text.configure(state="disabled", bg="#f0f0f0")
        self.target_path_text.pack(fill="x", pady=(0, 0))

        # 3. Open Directory Link
        tgt_links_frame = ttk.Frame(self)
        tgt_links_frame.pack(fill="x", anchor="w", pady=(0, 0))
        link_target_open = ttk.Label(
            tgt_links_frame, text="[open directory]", foreground="blue", cursor="hand2"
        )
        link_target_open.pack(side="right")
        link_target_open.bind("<Button-1>", lambda e: self.open_directory(self.target_path_str))

        # 4. Copy Source Model Button
        copy_source_btn = ttk.Button(
            self, text="Copy Source Model", command=self.on_copy_source_model
        )
        copy_source_btn.pack(side="left")

        self.load_target_models()

    def open_directory(self, path_str):
        subprocess.run(["open", path_str])

    def load_target_models(self):
        try:
            target_dir = get_target_models_dir()
            if target_dir.exists() and target_dir.is_dir():
                dirs = [item.name for item in target_dir.iterdir() if item.is_dir()]
                self.target_combo["values"] = sorted(dirs)
            else:
                self.target_combo["values"] = []
        except Exception as e:
            log("Setup", f"Error loading target models: {e}")
            self.target_combo["values"] = []

    def on_target_selected(self, event):
        val = self.target_var.get()
        if val:
            set_property("target_model", val)

    def on_copy_source_model(self):
        current_source = ""
        if self.get_current_source_func:
            current_source = self.get_current_source_func()

        if not current_source:
            messagebox.showinfo(
                "No Source Model", "Please select a source model to copy first.", parent=self
            )
            return

        suggested_name = f"{current_source}-MyModel"

        target_name = simpledialog.askstring(
            "Copy Source Model",
            "Enter a name for the new target model:",
            initialvalue=suggested_name,
            parent=self,
        )

        if target_name:
            source_dir = get_source_models_dir() / current_source
            target_dir = get_target_models_dir() / target_name

            if target_dir.exists():
                if not messagebox.askyesno(
                    "Target Exists",
                    f"Target model '{target_name}' already exists. Do you want to replace it?",
                    parent=self,
                ):
                    return
                shutil.rmtree(target_dir)

            try:
                shutil.copytree(source_dir, target_dir)
                log("Setup", f"Successfully copied source model '{current_source}' to target '{target_name}'.")

                selected_template = get_property("chat_template")
                if selected_template and selected_template != "None":
                    template_source_path = get_templates_dir() / selected_template
                    if template_source_path.exists():
                        template_target_path = target_dir / "chat_template.jinja"
                        shutil.copy(template_source_path, template_target_path)
                        log(
                            "Setup",
                            f"Copied selected chat template '{selected_template}' to target root as 'chat_template.jinja'.",
                        )
                    else:
                        log(
                            "Setup",
                            f"Warning: Selected chat template file '{selected_template}' not found at {template_source_path}.",
                        )
                else:
                    log("Setup", "No chat template selected ('None'); skipping chat_template.jinja copy.")

                self.load_target_models()
                self.target_var.set(target_name)
                set_property("target_model", target_name)
                messagebox.showinfo(
                    "Success", f"Successfully copied source model to target '{target_name}'.", parent=self
                )
            except Exception as e:
                log("Setup", f"Error copying source model or template: {e}")
                messagebox.showerror("Error", f"Failed to copy model:\n{e}", parent=self)