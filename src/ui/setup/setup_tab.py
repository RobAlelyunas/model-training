import subprocess
import tkinter as tk
from tkinter import ttk

from src.core.global_state import get_property, register_state_change_handler, set_property
from src.core.logging import log
from src.core.storage import get_logs_dir, get_templates_dir
from src.ui.setup.dataset_panel import DatasetPanel
from src.ui.setup.source_model_panel import SourceModelPanel
from src.ui.setup.target_model_panel import TargetModelPanel


class SetupTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        content_frame = ttk.Frame(self, padding=20)
        content_frame.pack(expand=True, fill="both")

        top_bar_frame = ttk.Frame(content_frame)
        top_bar_frame.pack(fill="x", pady=(0, 10))

        title_label = ttk.Label(
            top_bar_frame, text="Setup", font=("Helvetica", 14, "bold")
        )
        title_label.pack(side="left", anchor="w")

        # 2x2 Grid Container
        grid_frame = ttk.Frame(content_frame)
        grid_frame.pack(expand=True, fill="both", pady=(0, 10))

        grid_frame.columnconfigure(0, weight=1, uniform="col")
        grid_frame.columnconfigure(1, weight=1, uniform="col")
        grid_frame.rowconfigure(0, weight=1, uniform="row")
        grid_frame.rowconfigure(1, weight=1, uniform="row")

        # 1. Source Model Panel
        self.source_panel = SourceModelPanel(
            grid_frame, on_source_changed_callback=self.on_source_model_changed
        )
        self.source_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        # 2. Target Model Panel
        self.target_panel = TargetModelPanel(
            grid_frame, get_current_source_func=lambda: self.source_panel.source_var.get()
        )
        self.target_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # 3. Working Dataset Panel
        self.dataset_panel = DatasetPanel(grid_frame)
        self.dataset_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))

        # 4. Chat Template Panel
        template_frame = ttk.LabelFrame(grid_frame, text="4. Chat Template", padding=15)
        template_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))

        self.template_var = tk.StringVar(value="")
        self.template_combo = ttk.Combobox(
            template_frame, textvariable=self.template_var, state="readonly"
        )
        self.template_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)
        self.template_combo.bind("<Button-1>", lambda e: self.load_templates())

        template_path_str = str(get_templates_dir())

        self.template_path_text = tk.Text(
            template_frame, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1
        )
        self.template_path_text.insert("1.0", template_path_str)
        self.template_path_text.configure(state="disabled", bg="#f0f0f0")
        self.template_path_text.pack(fill="x", pady=(0, 0))

        tmpl_links_frame = ttk.Frame(template_frame)
        tmpl_links_frame.pack(fill="x", anchor="w", pady=(0, 18))
        link_tmpl_open = ttk.Label(
            tmpl_links_frame, text="[open directory]", foreground="blue", cursor="hand2"
        )
        link_tmpl_open.pack(side="right")
        link_tmpl_open.bind("<Button-1>", lambda e: self.open_directory(template_path_str))

        template_help_container = ttk.Frame(template_frame)
        template_help_container.pack(fill="x", pady=(0, 0))

        tmpl_line_frame = ttk.Frame(template_help_container)
        tmpl_line_frame.pack(fill="x", anchor="w")
        lbl_tmpl_reminder = ttk.Label(
            tmpl_line_frame,
            text="Note: Automatically selected to match source model."
                 " Override here for advanced use cases only.",
            wraplength=350,
        )
        lbl_tmpl_reminder.pack(side="left", anchor="w")

        # Bottom Bar: Logs Directory Path & Link
        logs_bar_frame = ttk.Frame(content_frame)
        logs_bar_frame.pack(fill="x", pady=(10, 0))
        logs_bar_frame.columnconfigure(0, weight=1)

        logs_path_str = str(get_logs_dir())

        link_logs_open = ttk.Label(
            logs_bar_frame, text="[open directory]", foreground="blue", cursor="hand2"
        )
        link_logs_open.pack(side="right", padx=(10, 0))
        link_logs_open.bind("<Button-1>", lambda e: self.open_directory(logs_path_str))

        self.logs_path_text = tk.Text(
            logs_bar_frame, height=1, font=("Courier", 11), wrap="none", relief="solid", bd=1
        )
        self.logs_path_text.insert("1.0", logs_path_str)
        self.logs_path_text.configure(state="disabled", bg="#f0f0f0")
        self.logs_path_text.pack(side="left", fill="x", expand=True)

        self.load_templates()
        self.sync_ui_with_state()
        register_state_change_handler(self.global_state_changed)

    def global_state_changed(self):
        pass

    def open_directory(self, path_str):
        subprocess.run(["open", path_str])

    def load_templates(self):
        try:
            template_dir = get_templates_dir()
            if template_dir.exists() and template_dir.is_dir():
                files = [
                    item.name
                    for item in template_dir.iterdir()
                    if item.is_file() and item.name.lower().endswith(".jinja")
                ]
                self.template_combo["values"] = ["None"] + sorted(files)
            else:
                self.template_combo["values"] = ["None"]
        except Exception as e:
            log("Setup", f"Error loading templates: {e}")
            self.template_combo["values"] = ["None"]

    def on_template_selected(self, event):
        val = self.template_var.get()
        if val:
            set_property("chat_template", val)

    def on_source_model_changed(self, source_model_name):
        """Auto-select matching template when source model selection changes."""
        self.load_templates()
        available_templates = self.template_combo["values"]
        if available_templates:
            source_lower = source_model_name.lower()
            matched_template = None

            families = ["qwen", "mistral", "gemma", "llama", "phi"]
            detected_family = None
            for fam in families:
                if fam in source_lower:
                    detected_family = fam
                    break

            if detected_family:
                for tmpl in available_templates:
                    if tmpl == "None":
                        continue
                    if detected_family in tmpl.lower():
                        matched_template = tmpl
                        break

            if not matched_template and len(available_templates) > 1:
                matched_template = available_templates[1]

            if matched_template:
                self.template_var.set(matched_template)
                set_property("chat_template", matched_template)

    def sync_ui_with_state(self):
        if src := get_property("source_model"):
            self.source_panel.source_var.set(src)
        if tgt := get_property("target_model"):
            self.target_panel.target_var.set(tgt)
        if ds := get_property("dataset"):
            self.dataset_panel.dataset_var.set(ds)
        if tmpl := get_property("chat_template"):
            self.template_var.set(tmpl)