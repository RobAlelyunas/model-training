import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from src.core.storage import (
    get_source_models_dir,
    get_target_models_dir,
    get_datasets_dir,
    get_templates_dir,
)
from src.core.global_state import set_property, get_property

class SetupTab(ttk.Frame):
    """
    Setup Tab: Full-width top panel for Hardware Verification with an interactive hyperlink, 
    followed by a 3-panel grid layout. Panel 5 (Chat Template) updated with reminder verbiage.
    """
    def __init__(self, parent):
        super().__init__(parent)
        
        # Main padding container
        content_frame = ttk.Frame(self, padding=20)
        content_frame.pack(expand=True, fill="both")

        # --- TOP LEVEL BAR: Title Only ---
        top_bar_frame = ttk.Frame(content_frame)
        top_bar_frame.pack(fill="x", pady=(0, 10))

        title_label = ttk.Label(
            top_bar_frame, 
            text="Environment Setup", 
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(side="left", anchor="w")

        # --- PANEL 1 (Full Width): 1. Verify My Mac ---
        verify_frame = ttk.LabelFrame(content_frame, text="1. Hardware Verification", padding=15)
        verify_frame.pack(fill="x", pady=(0, 10))

        verify_inner = ttk.Frame(verify_frame)
        verify_inner.pack(fill="x")

        # Hyperlink for hardware verification instead of a separate button
        link_verify = ttk.Label(verify_inner, text="Verify this Mac", foreground="blue", cursor="hand2")
        link_verify.pack(side="left")
        link_verify.bind("<Button-1>", lambda e: self.on_verify_mac())

        verify_text = ttk.Label(verify_inner, text=" and check its available memory.")
        verify_text.pack(side="left", anchor="w")

        # --- GRID CONTAINER FOR THE REMAINING 3 PANELS ---
        grid_frame = ttk.Frame(content_frame)
        grid_frame.pack(expand=True, fill="both")

        grid_frame.columnconfigure(0, weight=1, uniform="col")
        grid_frame.columnconfigure(1, weight=1, uniform="col")
        grid_frame.rowconfigure(0, weight=1, uniform="row")
        grid_frame.rowconfigure(1, weight=1, uniform="row")

        # --- PANEL 2 (Top-Left of Grid): Source Model ---
        source_frame = ttk.LabelFrame(grid_frame, text="2. Source Model", padding=15)
        source_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        # Dropdown directly at the top
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(
            source_frame, 
            textvariable=self.source_var, 
            state="readonly"
        )
        self.source_combo.pack(fill="x", anchor="w", pady=(0, 15))

        self.source_combo.bind("<<ComboboxSelected>>", self.on_source_selected)

        # Informative helper text container below
        help_container = ttk.Frame(source_frame)
        help_container.pack(fill="x", pady=(0, 0))

        # Line 1: "To make more source models available,"
        line1_frame = ttk.Frame(help_container)
        line1_frame.pack(fill="x", anchor="w", pady=(0, 1))

        lbl_line1 = ttk.Label(line1_frame, text="To make more source models available,")
        lbl_line1.pack(side="left")

        # Line 2: Hyperlink "download a starter model"
        line2_frame = ttk.Frame(help_container)
        line2_frame.pack(fill="x", anchor="w", pady=(0, 1))

        link_starter = ttk.Label(line2_frame, text="download a starter model", foreground="blue", cursor="hand2")
        link_starter.pack(side="left")
        link_starter.bind("<Button-1>", lambda e: messagebox.showinfo("Download", "Downloading starter model", parent=self))

        # Line 3: "or install a model from Hugging Face to:"
        line3_frame = ttk.Frame(help_container)
        line3_frame.pack(fill="x", anchor="w", pady=(0, 2))

        lbl_mid = ttk.Label(line3_frame, text="or install a model from Hugging Face to:")
        lbl_mid.pack(side="left")

        # Line 4: Compact path display with a small copy hyperlink
        source_path_str = str(get_source_models_dir())
        path_frame = ttk.Frame(help_container)
        path_frame.pack(fill="x", anchor="w", pady=(0, 2))

        self.path_entry = ttk.Entry(path_frame, font=("Courier", 9))
        self.path_entry.insert(0, source_path_str)
        self.path_entry.configure(state="readonly")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        link_copy = ttk.Label(path_frame, text="[copy]", foreground="blue", cursor="hand2")
        link_copy.pack(side="left")
        link_copy.bind("<Button-1>", lambda e: self.copy_to_clipboard(source_path_str))

        # Line 5: Refresh instruction with refresh hyperlink
        line5_frame = ttk.Frame(help_container)
        line5_frame.pack(fill="x", anchor="w")

        lbl_suffix = ttk.Label(line5_frame, text="Then click ")
        lbl_suffix.pack(side="left")

        link_refresh = ttk.Label(line5_frame, text="refresh", foreground="blue", cursor="hand2")
        link_refresh.pack(side="left")
        link_refresh.bind("<Button-1>", lambda e: self.load_source_models())

        lbl_end = ttk.Label(line5_frame, text=" to update.")
        lbl_end.pack(side="left")

        # --- PANEL 3 (Top-Right of Grid): Target Model ---
        target_frame = ttk.LabelFrame(grid_frame, text="3. Target Model", padding=15)
        target_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # Dropdown directly at the top
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(
            target_frame, 
            textvariable=self.target_var, 
            state="readonly"
        )
        self.target_combo.pack(fill="x", anchor="w", pady=(0, 15))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_selected)

        # Informative helper text container below
        target_help_container = ttk.Frame(target_frame)
        target_help_container.pack(fill="x", pady=(0, 0))

        # Line 1: Purpose statement
        t_line1_frame = ttk.Frame(target_help_container)
        t_line1_frame.pack(fill="x", anchor="w", pady=(0, 1))

        lbl_t_line1 = ttk.Label(t_line1_frame, text="A target is needed for interactive training.")
        lbl_t_line1.pack(side="left")

        # Line 2: Action instruction with hyperlink "copy the source model"
        t_line2_frame = ttk.Frame(target_help_container)
        t_line2_frame.pack(fill="x", anchor="w", pady=(0, 1))

        lbl_t_pre = ttk.Label(t_line2_frame, text="To get started on a new target, ")
        lbl_t_pre.pack(side="left")

        link_copy_source = ttk.Label(t_line2_frame, text="copy the source model", foreground="blue", cursor="hand2")
        link_copy_source.pack(side="left")
        link_copy_source.bind("<Button-1>", lambda e: self.on_copy_source_model())

        # Line 3: Location prompt
        t_line3_frame = ttk.Frame(target_help_container)
        t_line3_frame.pack(fill="x", anchor="w", pady=(0, 2))

        lbl_t_loc = ttk.Label(t_line3_frame, text="You can find target models in:")
        lbl_t_loc.pack(side="left")

        # Line 4: Compact path display for target models with copy hyperlink
        target_path_str = str(get_target_models_dir())
        t_path_frame = ttk.Frame(target_help_container)
        t_path_frame.pack(fill="x", anchor="w", pady=(0, 2))

        self.target_path_entry = ttk.Entry(t_path_frame, font=("Courier", 9))
        self.target_path_entry.insert(0, target_path_str)
        self.target_path_entry.configure(state="readonly")
        self.target_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        link_target_copy = ttk.Label(t_path_frame, text="[copy]", foreground="blue", cursor="hand2")
        link_target_copy.pack(side="left")
        link_target_copy.bind("<Button-1>", lambda e: self.copy_to_clipboard(target_path_str))

        # Line 5: Refresh instruction with refresh hyperlink
        t_line5_frame = ttk.Frame(target_help_container)
        t_line5_frame.pack(fill="x", anchor="w")

        lbl_t_suffix = ttk.Label(t_line5_frame, text="Then click ")
        lbl_t_suffix.pack(side="left")

        link_target_refresh = ttk.Label(t_line5_frame, text="refresh", foreground="blue", cursor="hand2")
        link_target_refresh.pack(side="left")
        link_target_refresh.bind("<Button-1>", lambda e: self.load_target_models())

        lbl_t_end = ttk.Label(t_line5_frame, text=" to update.")
        lbl_t_end.pack(side="left")

        # --- PANEL 4 (Bottom-Left of Grid): Dataset ---
        dataset_frame = ttk.LabelFrame(grid_frame, text="4. Dataset", padding=15)
        dataset_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(10, 0))

        # Dropdown directly at the top
        self.dataset_var = tk.StringVar()
        self.dataset_combo = ttk.Combobox(
            dataset_frame, 
            textvariable=self.dataset_var, 
            state="readonly"
        )
        self.dataset_combo.pack(fill="x", anchor="w", pady=(0, 15))
        self.dataset_combo.bind("<<ComboboxSelected>>", self.on_dataset_selected)

        # Informative helper text container below containing only the new empty dataset hyperlink
        dataset_help_container = ttk.Frame(dataset_frame)
        dataset_help_container.pack(fill="x", pady=(0, 0))

        ds_line_frame = ttk.Frame(dataset_help_container)
        ds_line_frame.pack(fill="x", anchor="w")

        link_new_dataset = ttk.Label(ds_line_frame, text="Generate a new empty dataset", foreground="blue", cursor="hand2")
        link_new_dataset.pack(side="left")
        link_new_dataset.bind("<Button-1>", lambda e: self.on_generate_empty_dataset())

        # --- PANEL 5 (Bottom-Right of Grid): Chat Template ---
        template_frame = ttk.LabelFrame(grid_frame, text="5. Chat Template", padding=15)
        template_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))

        # Dropdown directly at the top
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(
            template_frame, 
            textvariable=self.template_var, 
            state="readonly"
        )
        self.template_combo.pack(fill="x", anchor="w", pady=(0, 15))
        self.template_combo.bind("<<ComboboxSelected>>", self.on_template_selected)

        # Informative helper text container below with model family reminder verbiage
        template_help_container = ttk.Frame(template_frame)
        template_help_container.pack(fill="x", pady=(0, 0))

        tmpl_line_frame = ttk.Frame(template_help_container)
        tmpl_line_frame.pack(fill="x", anchor="w")

        lbl_tmpl_reminder = ttk.Label(
            tmpl_line_frame, 
            text="Select a chat template to match the source model family.",
            wraplength=350
        )
        lbl_tmpl_reminder.pack(side="left", anchor="w")

        # Initial population of all dropdowns
        self.refresh_all_dropdowns()

        # Pre-populate fields if values already exist in global state
        self.sync_ui_with_state()

    def on_verify_mac(self):
        """Placeholder hardware check action."""
        messagebox.showinfo("Hardware Check", "Mac verified.", parent=self)

    def on_copy_source_model(self):
        """Prompt user for target model name and handle copying action."""
        current_source = self.source_var.get()
        suggested_name = f"{current_source}-target" if current_source else "new-target"
        
        target_name = simpledialog.askstring(
            "Copy Source Model",
            "Enter a name for the new target model:",
            initialvalue=suggested_name,
            parent=self
        )
        
        if target_name:
            messagebox.showinfo("Copy Model", f"OK. Copying source model to target model: '{target_name}'", parent=self)
            # Future implementation for actual copy mechanism goes here

    def on_generate_empty_dataset(self):
        """Prompt user for new dataset name, create empty dataset, refresh, and auto-select it."""
        dataset_name = simpledialog.askstring(
            "Generate Empty Dataset",
            "Enter a name for the new dataset (e.g., custom_data.json):",
            initialvalue="new_dataset.json",
            parent=self
        )
        
        if dataset_name:
            if not dataset_name.endswith(('.json', '.jsonl', '.txt')):
                dataset_name += ".json"

            # TODO: Add actual file creation logic in datasets directory here
            
            # Refresh the dataset dropdown list automatically
            self.load_datasets()
            
            # Automatically select the newly created dataset in the dropdown and state
            self.dataset_var.set(dataset_name)
            set_property("dataset", dataset_name)

    def copy_to_clipboard(self, text):
        """Copies the given text to the system clipboard."""
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Directory path copied to clipboard.", parent=self)

    def refresh_all_dropdowns(self):
        """Scans all storage directories and updates all four dropdown options at once."""
        self.load_source_models()
        self.load_target_models()
        self.load_datasets()
        self.load_templates()

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
            print(f"[Setup] Error loading source models: {e}")
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
            print(f"[Setup] Error loading target models: {e}")
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
            print(f"[Setup] Error loading datasets: {e}")
            self.dataset_combo['values'] = []

    def load_templates(self):
        """Scans the templates directory and updates dropdown options."""
        try:
            template_dir = get_templates_dir()
            if template_dir.exists() and template_dir.is_dir():
                files = [item.name for item in template_dir.iterdir() if item.is_file()]
                self.template_combo['values'] = sorted(files)
            else:
                self.template_combo['values'] = []
        except Exception as e:
            print(f"[Setup] Error loading templates: {e}")
            self.template_combo['values'] = []

    def on_source_selected(self, event):
        val = self.source_var.get()
        if val:
            set_property("source_model", val)

    def on_target_selected(self, event):
        val = self.target_var.get()
        if val:
            set_property("target_model", val)

    def on_dataset_selected(self, event):
        val = self.dataset_var.get()
        if val:
            set_property("dataset", val)

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