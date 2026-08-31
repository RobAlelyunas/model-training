import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import subprocess
import shutil
import json
from src.core.storage import (
    get_source_models_dir,
    get_target_models_dir,
    get_datasets_dir,
    get_templates_dir,
    get_logs_dir,
)
from src.core.global_state import set_property, get_property
from src.core.logging import log

class SetupTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Main padding container
        content_frame = ttk.Frame(self, padding=20)
        content_frame.pack(expand=True, fill="both")

        top_bar_frame = ttk.Frame(content_frame)
        top_bar_frame.pack(fill="x", pady=(0, 10))

        title_label = ttk.Label(
            top_bar_frame, 
            text="Setup", 
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(side="left", anchor="w")

        # Main grid container for the 4 panels
        grid_frame = ttk.Frame(content_frame)
        grid_frame.pack(expand=True, fill="both", pady=(0, 10))

        grid_frame.columnconfigure(0, weight=1, uniform="col")
        grid_frame.columnconfigure(1, weight=1, uniform="col")
        grid_frame.rowconfigure(0, weight=1, uniform="row")
        grid_frame.rowconfigure(1, weight=1, uniform="row")

        # =========================================================================
        # --- PANEL 1 (Top-Left of Grid): Source Model ---
        # =========================================================================
        source_frame = ttk.LabelFrame(grid_frame, text="1. Source Model", padding=15)
        source_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        # 1. Dropdown at the top
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(
            source_frame, 
            textvariable=self.source_var, 
            state="readonly"
        )
        self.source_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.source_combo.bind("<<ComboboxSelected>>", self.on_source_selected)
        self.source_combo.bind("<Button-1>", lambda e: self.load_source_models())
        
        # 2. Directory path box immediately below dropdown
        source_path_str = str(get_source_models_dir())
        self.path_text = tk.Text(source_frame, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1)
        self.path_text.insert("1.0", source_path_str)
        self.path_text.configure(state="disabled", bg="#f0f0f0")
        self.path_text.pack(fill="x", pady=(0, 0))

        # 3. Left-justified links line underneath the path box
        src_links_frame = ttk.Frame(source_frame)
        src_links_frame.pack(fill="x", anchor="w", pady=(0, 5))
        link_open = ttk.Label(src_links_frame, text="[open directory]", foreground="blue", cursor="hand2")
        link_open.pack(side="right")
        link_open.bind("<Button-1>", lambda e: self.open_directory(source_path_str))

        # 4. Download starter model button
        download_starter_btn = ttk.Button(source_frame, text="Download Starter Model", command=self.on_download_starter_model)
        download_starter_btn.pack(side="left")

        # =========================================================================
        # --- PANEL 2 (Top-Right of Grid): Target Model ---
        # =========================================================================
        target_frame = ttk.LabelFrame(grid_frame, text="2. Target Model", padding=15)
        target_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # 1. Dropdown at the top
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(
            target_frame, 
            textvariable=self.target_var,
            state="readonly"
        )
        self.target_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_selected)
        self.target_combo.bind("<Button-1>", lambda e: self.load_target_models())

        target_path_str = str(get_target_models_dir())

        # 2. Directory path box immediately below dropdown
        self.target_path_text = tk.Text(target_frame, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1)
        self.target_path_text.insert("1.0", target_path_str)
        self.target_path_text.configure(state="disabled", bg="#f0f0f0")
        self.target_path_text.pack(fill="x", pady=(0, 0))

        # 3. Left-justified links line underneath the path box
        tgt_links_frame = ttk.Frame(target_frame)
        tgt_links_frame.pack(fill="x", anchor="w", pady=(0, 0))
        link_target_open = ttk.Label(tgt_links_frame, text="[open directory]", foreground="blue", cursor="hand2")
        link_target_open.pack(side="right")
        link_target_open.bind("<Button-1>", lambda e: self.open_directory(target_path_str))

        # 4. Copy Source Model button
        copy_source_btn = ttk.Button(target_frame, text="Copy Source Model", command=self.on_copy_source_model)
        copy_source_btn.pack(side="left")

        # =========================================================================
        # --- PANEL 3 (Bottom-Left of Grid): Dataset ---
        # =========================================================================
        dataset_frame = ttk.LabelFrame(grid_frame, text="3. Dataset", padding=15)
        dataset_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))

        # 1. Dropdown at the top
        self.dataset_var = tk.StringVar()
        self.dataset_combo = ttk.Combobox(
            dataset_frame, 
            textvariable=self.dataset_var, 
            state="readonly"
        )
        self.dataset_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.dataset_combo.bind("<<ComboboxSelected>>", self.on_dataset_selected)
        self.dataset_combo.bind("<Button-1>", lambda e: self.load_datasets())

        # 2. Directory path box immediately below dropdown
        dataset_path_str = str(get_datasets_dir())
        self.dataset_path_text = tk.Text(dataset_frame, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1)
        self.dataset_path_text.insert("1.0", dataset_path_str)
        self.dataset_path_text.configure(state="disabled", bg="#f0f0f0")
        self.dataset_path_text.pack(fill="x", pady=(0, 0))

        # 3. Left-justified links line underneath the path box
        ds_links_frame = ttk.Frame(dataset_frame)
        ds_links_frame.pack(fill="x", anchor="w", pady=(0, 0))
        link_ds_open = ttk.Label(ds_links_frame, text="[open directory]", foreground="blue", cursor="hand2")
        link_ds_open.pack(side="right")
        link_ds_open.bind("<Button-1>", lambda e: self.open_directory(dataset_path_str))

         # 4. Create New Dataset button
        new_dataset_btn = ttk.Button(dataset_frame, text="Create New Dataset", command=self.on_generate_empty_dataset)
        new_dataset_btn.pack(side="left")

        # =========================================================================
        # --- PANEL 4 (Bottom-Right of Grid): Chat Template ---
        # =========================================================================
        template_frame = ttk.LabelFrame(grid_frame, text="4. Chat Template", padding=15)
        template_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))

        # 1. Dropdown at the top
        self.template_var = tk.StringVar(value="")
        self.template_combo = ttk.Combobox(
            template_frame, 
            textvariable=self.template_var, 
            state="readonly"
        )
        self.template_combo.pack(fill="x", anchor="w", pady=(0, 18))
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)
        self.template_combo.bind("<Button-1>", lambda e: self.load_templates())

        template_path_str = str(get_templates_dir())

        # 2. Directory path box immediately below dropdown
        self.template_path_text = tk.Text(template_frame, height=3, font=("Courier", 12), wrap="char", relief="solid", bd=1)
        self.template_path_text.insert("1.0", template_path_str)
        self.template_path_text.configure(state="disabled", bg="#f0f0f0")
        self.template_path_text.pack(fill="x", pady=(0, 0))

        # 3. links line underneath the path box
        tmpl_links_frame = ttk.Frame(template_frame)
        tmpl_links_frame.pack(fill="x", anchor="w", pady=(0, 18))
        link_tmpl_open = ttk.Label(tmpl_links_frame, text="[open directory]", foreground="blue", cursor="hand2")
        link_tmpl_open.pack(side="right")
        link_tmpl_open.bind("<Button-1>", lambda e: self.open_directory(template_path_str))

        # 4. Informative helper text container
        template_help_container = ttk.Frame(template_frame)
        template_help_container.pack(fill="x", pady=(0, 0))

        tmpl_line_frame = ttk.Frame(template_help_container)
        tmpl_line_frame.pack(fill="x", anchor="w")
        lbl_tmpl_reminder = ttk.Label(
            tmpl_line_frame, 
            text="Note: Automatically selected to match source model."
                 " Override here for advanced use cases only.",
            wraplength=350
        )
        lbl_tmpl_reminder.pack(side="left", anchor="w")

        # =========================================================================
        # --- COMPACT BOTTOM BAR: Logs Directory Path & Link ---
        # =========================================================================
        logs_bar_frame = ttk.Frame(content_frame)
        logs_bar_frame.pack(fill="x", pady=(10, 0))
        logs_bar_frame.columnconfigure(0, weight=1)

        logs_path_str = str(get_logs_dir())

        # Hyperlink on the right side
        link_logs_open = ttk.Label(logs_bar_frame, text="[open directory]", foreground="blue", cursor="hand2")
        link_logs_open.pack(side="right", padx=(10, 0))
        link_logs_open.bind("<Button-1>", lambda e: self.open_directory(logs_path_str))

        # Narrow single-line copyable text box for the path
        self.logs_path_text = tk.Text(logs_bar_frame, height=1, font=("Courier", 11), wrap="none", relief="solid", bd=1)
        self.logs_path_text.insert("1.0", logs_path_str)
        self.logs_path_text.configure(state="disabled", bg="#f0f0f0")
        self.logs_path_text.pack(side="left", fill="x", expand=True)

        # Initial population of all dropdowns
        self.load_source_models()
        self.load_target_models()
        self.load_datasets()
        self.load_templates()

        # Pre-populate fields if values already exist in global state
        self.sync_ui_with_state()

    def on_download_starter_model(self):
        messagebox.showinfo("downloading", "downloading")

    def on_copy_source_model(self):
        """Prompt user for target model name, copy source folder, handle collisions, copy template if set, and select it."""
        current_source = self.source_var.get()
        if not current_source:
            messagebox.showinfo("No Source Model", "Please select a source model to copy first.", parent=self)
            return
        
        suggested_name = f"{current_source}-MyModel"
        
        target_name = simpledialog.askstring(
            "Copy Source Model",
            "Enter a name for the new target model:",
            initialvalue=suggested_name,
            parent=self
        )
        
        if target_name:
            source_dir = get_source_models_dir() / current_source
            target_dir = get_target_models_dir() / target_name
            
            if target_dir.exists():
                if not messagebox.askyesno("Target Exists", f"Target model '{target_name}' already exists. Do you want to replace it?", parent=self):
                    return
                shutil.rmtree(target_dir)
                
            try:
                # 1. Copy source model directory to target directory
                shutil.copytree(source_dir, target_dir)
                log("Setup", f"Successfully copied source model '{current_source}' to target '{target_name}'.")

                # 2. Check if a valid chat template is selected (ignoring explicit "None")
                selected_template = get_property("chat_template")
                if selected_template and selected_template != "None":
                    template_source_path = get_templates_dir() / selected_template
                    if template_source_path.exists():
                        template_target_path = target_dir / "chat_template.jinja"
                        shutil.copy(template_source_path, template_target_path)
                        log("Setup", f"Copied selected chat template '{selected_template}' to target root as 'chat_template.jinja'.")
                    else:
                        log("Setup", f"Warning: Selected chat template file '{selected_template}' not found at {template_source_path}.")
                else:
                    log("Setup", "No chat template selected ('None'); skipping chat_template.jinja copy.")

                self.load_target_models()
                self.target_var.set(target_name)
                set_property("target_model", target_name)
                messagebox.showinfo("Success", f"Successfully copied source model to target '{target_name}'.", parent=self)
            except Exception as e:
                log("Setup", f"Error copying source model or template: {e}")
                messagebox.showerror("Error", f"Failed to copy model:\n{e}", parent=self)

    def on_generate_empty_dataset(self):
        """Prompt user for new dataset name, handle collision checking, create initial record, and auto-select it."""
        dataset_name = simpledialog.askstring(
            "Generate Empty Dataset",
            "Enter a name for the new dataset:",
            initialvalue="new_working_dataset.jsonl",
            parent=self
        )
        
        if dataset_name:
            if not dataset_name.endswith('.jsonl'):
                dataset_name += ".jsonl"

            file_path = get_datasets_dir() / dataset_name
            
            if file_path.exists():
                if not messagebox.askyesno("File Exists", f"Dataset '{dataset_name}' already exists. Do you want to replace it?", parent=self):
                    return

            try:
                # Ensure parent directory exists and write initial record
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

    def open_directory(self, path_str):
        subprocess.run(["open", path_str])

    def load_source_models(self):
        """Scans the source models directory and updates dropdown options."""
        try:
            source_dir = get_source_models_dir()
            if source_dir.exists() and source_dir.is_dir():
                dirs = [item.name for item in source_dir.iterdir() if item.is_dir()]
                self.source_combo['values'] = sorted(dirs)
            else:
                self.source_combo['values'] = []
        except Exception as e:
            log("Setup", f"Error loading source models: {e}")
            self.source_combo['values'] = []

    def load_target_models(self):
        """Scans the target models directory and updates dropdown options."""
        try:
            target_dir = get_target_models_dir()
            if target_dir.exists() and target_dir.is_dir():
                dirs = [item.name for item in target_dir.iterdir() if item.is_dir()]
                self.target_combo['values'] = sorted(dirs)
            else:
                self.target_combo['values'] = []
        except Exception as e:
            log("Setup", f"Error loading target models: {e}")
            self.target_combo['values'] = []

    def load_datasets(self):
        """Scans the datasets directory and updates dropdown options."""
        try:
            dataset_dir = get_datasets_dir()
            if dataset_dir.exists() and dataset_dir.is_dir():
                files = [item.name for item in dataset_dir.iterdir() if item.is_file()]
                self.dataset_combo['values'] = sorted(files)
            else:
                self.dataset_combo['values'] = []
        except Exception as e:
            log("Setup", f"Error loading datasets: {e}")
            self.dataset_combo['values'] = []

    def load_templates(self):
        """Scans the templates directory for .jinja files and updates dropdown options with 'None' prepended."""
        try:
            template_dir = get_templates_dir()
            if template_dir.exists() and template_dir.is_dir():
                files = [
                    item.name for item in template_dir.iterdir() 
                    if item.is_file() and item.name.lower().endswith(".jinja")
                ]
                self.template_combo['values'] = ["None"] + sorted(files)
            else:
                self.template_combo['values'] = ["None"]
        except Exception as e:
            log("Setup", f"Error loading templates: {e}")
            self.template_combo['values'] = ["None"]

    def on_source_selected(self, event):
        val = self.source_var.get()
        if val:
            set_property("source_model", val)
            
            # Automatically match the chat template based on the model family prefix
            self.load_templates() # Refresh available templates first
            available_templates = self.template_combo['values']
            if available_templates:
                source_lower = val.lower()
                matched_template = None
                
                # Check for model family keywords in the source model name
                families = ["qwen", "mistral", "gemma", "llama", "phi"]
                detected_family = None
                for fam in families:
                    if fam in source_lower:
                        detected_family = fam
                        break
                
                # Find a template filename that starts with or contains the detected family name
                if detected_family:
                    for tmpl in available_templates:
                        if tmpl == "None":
                            continue
                        if detected_family in tmpl.lower():
                            matched_template = tmpl
                            break
                
                # Fallback to first actual template if specific family match fails
                if not matched_template and len(available_templates) > 1:
                    matched_template = available_templates[1]
                
                if matched_template:
                    self.template_var.set(matched_template)
                    set_property("chat_template", matched_template)

    def on_target_selected(self, event):
        val = self.target_var.get()
        if val:
            set_property("target_model", val)

    def on_dataset_selected(self, event):
        val = self.dataset_var.get()
        if val:
            set_property("dataset", val)
            set_property("dataset_version", 0)

    def on_template_selected(self, event):
        val = self.template_var.get()
        if val:
            set_property("chat_template", val)

    def sync_ui_with_state(self):
        """Pulls existing state properties if already configured."""
        if src := get_property("source_model"):
            self.source_var.set(src)
        if tgt := get_property("target_model"):
            self.target_var.set(tgt)
        if ds := get_property("dataset"):
            self.dataset_var.set(ds)
        if tmpl := get_property("chat_template"):
            self.template_var.set(tmpl)