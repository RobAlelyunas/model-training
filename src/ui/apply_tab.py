import tkinter as tk
from tkinter import messagebox, ttk
from src.services.inference_engine import inference_engine
from src.services.run_command import TaskHandle
from src.services.training_service import training_service
from src.ui.ui_theme import (
    LOG_BG, 
    LOG_FG_DEFAULT, 
    LOG_FG_PIPELINE, 
    LOG_FG_CONTROLLER, 
    LOG_FG_ERROR
)
from src.core.global_state import get_property, register_state_change_handler, set_property
from src.ui.ui_helpers import requires, run_background
from src.core.logging import log


class ApplyTab(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.model_mapping = {}
        self.task_handle = None

        self.create_widgets()
        register_state_change_handler(self.global_state_changed)

    def global_state_changed(self):
        pass

    def create_widgets(self):
        # Top Frame: Status Header & Controls
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.status_label = ttk.Label(
            top_frame, text="Apply the dataset to create a new target model.", font=("Arial", 11, "bold")
        )
        self.status_label.pack(side="left", padx=5)

        # Buttons Container on the Right
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side="right", padx=5)

        self.start_button = ttk.Button(
            btn_frame, text="Run", command=self.start_workflow
        )
        self.start_button.pack(side="left", padx=2)

        self.cancel_button = ttk.Button(
            btn_frame, text="Stop", command=self.confirm_cancel, state=tk.DISABLED
        )
        self.cancel_button.pack(side="left", padx=2)

        # Hyperparameters Frame (Organized into grid rows for clean alignment)
        params_frame = ttk.LabelFrame(self, text="Training Hyperparameters", padding=12)
        params_frame.pack(fill="x", padx=15, pady=5)

        # Sub-header bar inside params frame to hold the "Auto Set" button cleanly on the right
        params_header_frame = ttk.Frame(params_frame)
        params_header_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(params_header_frame, text="Configure training settings or auto-calculate based on environment:", font=("Arial", 9, "italic")).pack(side="left", padx=2)
        
        self.auto_set_button = ttk.Button(
            params_header_frame, text="Auto Set", command=self.auto_set_parameters, width=10
        )
        self.auto_set_button.pack(side="right", padx=2)

        # Configure a custom ttk style to right-justify text inside Entry widgets
        style = ttk.Style()
        style.configure("RightEntry.TEntry", justify="right")

        # Row 0: Iterations, Batch Size, Layers, Learning Rate (Highest order to lowest order left-to-right)
        row0_frame = ttk.Frame(params_frame)
        row0_frame.pack(fill="x", pady=(0, 8))

        # 1. Iterations
        ttk.Label(row0_frame, text="Iterations:").pack(side="left", padx=(0, 2))
        try:
            default_iters = str(get_property("lora_iters"))
        except KeyError:
            default_iters = "150"
        self.iters_var = tk.StringVar(value=default_iters)
        self.iters_entry = ttk.Entry(row0_frame, textvariable=self.iters_var, width=6, style="RightEntry.TEntry")
        self.iters_entry.pack(side="left", padx=(0, 15))
        self.iters_entry.bind("<FocusOut>", lambda e: self.validate_and_save_int("lora_iters", self.iters_var, "Iterations"))

        # 2. Batch Size
        ttk.Label(row0_frame, text="Batch Size:").pack(side="left", padx=(0, 2))
        try:
            default_batch = str(get_property("lora_batch_size"))
        except KeyError:
            default_batch = "1"
        self.batch_var = tk.StringVar(value=default_batch)
        self.batch_entry = ttk.Entry(row0_frame, textvariable=self.batch_var, width=5, style="RightEntry.TEntry")
        self.batch_entry.pack(side="left", padx=(0, 15))
        self.batch_entry.bind("<FocusOut>", lambda e: self.validate_and_save_int("lora_batch_size", self.batch_var, "Batch Size"))

        # 3. Layers
        ttk.Label(row0_frame, text="Layers:").pack(side="left", padx=(0, 2))
        try:
            default_layers = str(get_property("lora_num_layers"))
        except KeyError:
            default_layers = "8"
        self.layers_var = tk.StringVar(value=default_layers)
        self.layers_entry = ttk.Entry(row0_frame, textvariable=self.layers_var, width=5, style="RightEntry.TEntry")
        self.layers_entry.pack(side="left", padx=(0, 15))
        self.layers_entry.bind("<FocusOut>", lambda e: self.validate_and_save_int("lora_num_layers", self.layers_var, "Layers"))

        # 4. Learning Rate
        ttk.Label(row0_frame, text="Learning Rate:").pack(side="left", padx=(0, 2))
        try:
            default_lr = str(get_property("lora_learning_rate"))
        except KeyError:
            default_lr = "2e-05"
        self.lr_var = tk.StringVar(value=default_lr)
        self.lr_entry = ttk.Entry(row0_frame, textvariable=self.lr_var, width=10, style="RightEntry.TEntry")
        self.lr_entry.pack(side="left", padx=(0, 10))
        self.lr_entry.bind("<FocusOut>", lambda e: self.validate_and_save_float("lora_learning_rate", self.lr_var, "Learning Rate"))

        # Row 1: Quantization Settings (Checkbox and Quant Bits)
        row1_frame = ttk.Frame(params_frame)
        row1_frame.pack(fill="x")

        # 5. Perform Quantization (Checkbox)
        try:
            default_quant_bool = bool(get_property("perform_quantization"))
        except KeyError:
            default_quant_bool = False
        self.quant_var = tk.BooleanVar(value=default_quant_bool)
        self.quant_chk = ttk.Checkbutton(
            row1_frame, 
            text="Perform Quantization", 
            variable=self.quant_var,
            command=self.save_hyperparameters
        )
        self.quant_chk.pack(side="left", padx=(0, 20))

        # 6. Quantization Bits
        ttk.Label(row1_frame, text="Quant Bits:").pack(side="left", padx=(0, 2))
        try:
            default_qbits = str(get_property("quantization_bits"))
        except KeyError:
            default_qbits = "4"
        self.qbits_var = tk.StringVar(value=default_qbits)
        self.qbits_entry = ttk.Entry(row1_frame, textvariable=self.qbits_var, width=5, style="RightEntry.TEntry")
        self.qbits_entry.pack(side="left", padx=(0, 10))
        self.qbits_entry.bind("<FocusOut>", lambda e: self.validate_and_save_int("quantization_bits", self.qbits_var, "Quant Bits"))

        # Center Frame: Real-time Log Streaming Window
        log_frame = ttk.LabelFrame(self, text="Execution Logs")
        log_frame.pack(expand=True, fill="both", padx=10, pady=5)

        self.text_box = tk.Text(
            log_frame, wrap="word", bg=LOG_BG, fg=LOG_FG_DEFAULT, font=("Courier", 10)
        )
        self.text_box.pack(side="left", expand=True, fill="both", padx=5, pady=5)

        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.text_box.yview
        )
        scrollbar.pack(side="right", fill="y", pady=5)
        self.text_box.configure(yscrollcommand=scrollbar.set)

        # Map theme colors to distinct text box tags
        self.text_box.tag_config("stdout_tag", foreground=LOG_FG_DEFAULT)
        self.text_box.tag_config("pipeline_tag", foreground=LOG_FG_PIPELINE, font=("Courier", 10, "bold"))
        self.text_box.tag_config("controller_tag", foreground=LOG_FG_CONTROLLER)
        self.text_box.tag_config("error_tag", foreground=LOG_FG_ERROR, font=("Courier", 10, "bold"))

    @requires("source_model", "target_model", "dataset")
    def auto_set_parameters(self):
        """Placeholder for automatically calculating and updating optimal hyperparameters."""
        messagebox.showinfo(
            "Auto Set Hyperparameters",
            "TODO: Automatically calculate optimal parameters based on available RAM, source model size, and dataset record count.",
            parent=self
        )

    def validate_and_save_int(self, prop_name, var, field_label):
        """Validates that an entry is a positive integer or zero, updating global state or reverting."""
        val_str = var.get().strip()
        try:
            val_int = int(val_str)
            if val_int < 0:
                raise ValueError("Must be non-negative")
            set_property(prop_name, val_int)
        except (ValueError, TypeError):
            messagebox.showerror(
                "Invalid Input",
                f"Please enter a valid positive integer for {field_label}.",
                parent=self
            )
            # Revert to last known valid property value
            try:
                var.set(str(get_property(prop_name)))
            except KeyError:
                var.set("0")

    def validate_and_save_float(self, prop_name, var, field_label):
        """Validates that an entry is a valid floating point number (including scientific notation), updating state or reverting."""
        val_str = var.get().strip()
        try:
            val_float = float(val_str)
            set_property(prop_name, val_str)
        except (ValueError, TypeError):
            messagebox.showerror(
                "Invalid Input",
                f"Please enter a valid floating-point number for {field_label} (e.g., 2e-05 or 0.0001).",
                parent=self
            )
            # Revert to last known valid property value
            try:
                var.set(str(get_property(prop_name)))
            except KeyError:
                var.set("2e-05")

    def save_hyperparameters(self):
        """Saves current values from checkboxes to global state."""
        set_property("perform_quantization", self.quant_var.get())

    @requires("source_model", "target_model", "dataset", "chat_template")
    def start_workflow(self):
        """Kicks off the complete workflow lifecycle cleanly using the background helper."""
        self.save_hyperparameters()

        # Instantiate TaskHandle and attach the text widget
        self.task_handle = TaskHandle()
        self.task_handle.set_widget(self.text_box)

        # Clear text display for new run
        self.text_box.delete("1.0", tk.END)

        # Log initial configuration
        dataset_path = get_property("dataset")
        source_model_path = get_property("source_model")
        iters = get_property("lora_iters")
        batch_size = get_property("lora_batch_size")
        num_layers = get_property("lora_num_layers")
        learning_rate = get_property("lora_learning_rate")

        log(
            "ApplyTab",
            f"Applying dataset '{dataset_path}' to source model '{source_model_path}' "
            f"with hyperparameters: iters={iters}, batch_size={batch_size}, "
            f"num_layers={num_layers}, learning_rate={learning_rate}",
            self.task_handle
        )

        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        # Pre-pipeline step
        self.status_label.config(text="Preparing: Unloading inference model to save memory...")
        log("PIPELINE", "=== PRE-PIPELINE: UNLOADING INFERENCE MODEL TO SAVE MEMORY ===", self.task_handle)
        inference_engine.unload_model()

        # Start pipeline step
        self.status_label.config(text="Running training pipeline...")
        log("PIPELINE", "=== STARTING TRAINING PIPELINE ===", self.task_handle)

        pipeline_succeeded = [True]

        def background_pipeline_task():
            try:
                training_service.apply_pipeline(self.task_handle)
            except Exception as e:
                pipeline_succeeded[0] = False
                raise e
            return True

        def on_pipeline_complete(success):
            self.start_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)

            # Check explicit cancellation status first
            if self.task_handle and self.task_handle.is_cancelled():
                self.status_label.config(text="Pipeline terminated by user.")
                log(
                    "PIPELINE",
                    "=== PIPELINE TERMINATED BY USER: The process was stopped before completion. "
                    "Target model artifacts may be incomplete or invalid. ===",
                    self.task_handle
                )
                return

            if pipeline_succeeded[0] and success:
                log("ApplyTab", "Successfully trained model workflow completed.", self.task_handle)
                self.status_label.config(text="Finishing: setting target model and loading inference model...")
                target_model = get_property("target_model")
                log("PIPELINE", f"=== POST-PIPELINE: Set Target Model to '{target_model}' ===", self.task_handle)
                set_property("target_model", target_model)
                
                try:
                    inference_engine.load_model()
                    self.status_label.config(text="Pipeline completed successfully!")
                    log("PIPELINE", "=== PIPELINE COMPLETED SUCCESSFULLY ===", self.task_handle)
                except Exception as e:
                    log("ApplyTab", f"[ERROR] Failed to reload model: {e}", self.task_handle)
                    messagebox.showerror("Error", f"Failed to load model:\n{e}")
            else:
                self.status_label.config(text="Pipeline failed.")
                log("ApplyTab", "[ERROR] Model training exited with error or failed.", self.task_handle)

        run_background(self, background_pipeline_task, on_pipeline_complete)

    def confirm_cancel(self):
        if not self.task_handle:
            return
        response = messagebox.askyesno(
            "Confirm Cancellation",
            "Terminate current step and end the pipeline?",
        )
        if response:
            self.status_label.config(text="Stopping after current step...")
            log("ApplyTab", "[User Action] Stop requested. Waiting for cancellation...", self.task_handle)
            self.task_handle.cancel()