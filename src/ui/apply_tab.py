import tkinter as tk
from tkinter import messagebox, ttk
import sys
from src.services.inference_engine import inference_engine
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


class StdoutRedirector:
    """Helper to capture standard output and funnel it into the Tkinter text widget with theme colors."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if not message:
            return
            
        if "[PIPELINE]" in message:
            tag = "pipeline_tag"
        elif "[ProcessController]" in message or "[InferenceEngine]" in message or "[TrainingService]" in message:
            tag = "controller_tag"
        elif "Error" in message or "FAILED" in message or "Exception" in message:
            tag = "error_tag"
        else:
            tag = "stdout_tag"

        self.text_widget.insert(tk.END, message, tag)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class ApplyTab(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        self.original_stdout = None
        self.model_mapping = {}

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
            set_property(prop_name, val_str)  # Keep string representation (e.g. "2e-05") or float depending on preference
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

    @requires("source_model","target_model","dataset","chat_template")
    def start_workflow(self):
        """Kicks off the complete workflow lifecycle cleanly using the background helper."""
        # Ensure checkbox state is saved
        self.save_hyperparameters()

        # Log summary statement BEFORE standard out gets redirected to the text window
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
            f"num_layers={num_layers}, learning_rate={learning_rate}"
        )

        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)
        
        # Redirect standard output so all log statements stream directly into the text box
        self.original_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.text_box)

        # 1. Pre-Pipeline Tasks (Unload inference model)
        self.status_label.config(text="Preparing: Unloading inference model...")
        self.text_box.insert(tk.END, "=== PRE-PIPELINE: UNLOADING INFERENCE MODEL ===\n", "pipeline_tag")
        inference_engine.unload_model()
        
        self.status_label.config(text="Running training pipeline...")
        self.text_box.insert(tk.END, "=== STARTING TRAINING PIPELINE ===\n", "pipeline_tag")

        # Track pipeline health for post-execution logging
        pipeline_succeeded = [True]

        # Define background task (now completely synchronous and blocking)
        def background_pipeline_task():
            try:
                training_service.apply_pipeline()
            except Exception as e:
                pipeline_succeeded[0] = False
                raise e
            return True

        # Define UI cleanup callback when background execution finishes
        def on_pipeline_complete(success):
            if self.original_stdout:
                sys.stdout = self.original_stdout

            # Log completion or error status via log() now that stdout redirection is undone
            if pipeline_succeeded[0] and success:
                log("ApplyTab", "Successfully trained model workflow completed.")
            else:
                log("ApplyTab", "Model training exited with error or failed.")

            self.start_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)

            self.status_label.config(text="Finishing: setting target model and loading inference model...")
            target_model = get_property("target_model")
            self.text_box.insert(tk.END, f"\n=== POST-PIPELINE: Set Target Model to '{target_model}' ===\n", "pipeline_tag")
            set_property("target_model", target_model)
            try:
                inference_engine.load_model()
                self.status_label.config(text="Pipeline completed successfully!")
                self.text_box.insert(tk.END, "=== PIPELINE COMPLETED SUCCESSFULLY ===\n", "pipeline_tag")
            except Exception as e:
                self.text_box.insert(tk.END, f"[Error] Failed to reload model: {e}\n", "error_tag")
                messagebox.showerror("Error", f"Failed to load model:\n{e}")

        # Fire it off via the clean background helper
        run_background(self, background_pipeline_task, on_pipeline_complete)

    def confirm_cancel(self):
        """Requests graceful pipeline halt after the current step finishes."""
        response = messagebox.askyesno(
            "Confirm Stop",
            "This will let the current step finish and then safely stop the pipeline.\nDo you want to proceed?",
            icon="warning"
        )

        if response:
            self.status_label.config(text="Stopping after current step...")
            self.text_box.insert(tk.END, "\n[User Action] Stop requested. Waiting for current step to complete...\n", "error_tag")
            training_service.request_cancel()