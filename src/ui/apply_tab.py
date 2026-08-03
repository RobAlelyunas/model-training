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
from src.global_state import register_state_change_handler


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

        self.active_controller = None
        self.is_cancelled_by_user = False
        self.original_stdout = None
        
        # Mapping for display string -> actual directory path name
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
            top_frame, text="Ready to apply training pipeline.", font=("Arial", 11, "bold")
        )
        self.status_label.pack(side="left", padx=5)

        # Buttons Container on the Right
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side="right", padx=5)

        self.start_button = ttk.Button(
            btn_frame, text="Apply Training", command=self.start_workflow
        )
        self.start_button.pack(side="left", padx=2)

        self.cancel_button = ttk.Button(
            btn_frame, text="Stop", command=self.confirm_cancel, state=tk.DISABLED
        )
        self.cancel_button.pack(side="left", padx=2)

        # Custom Target Model Options Frame
        custom_frame = ttk.Frame(self)
        custom_frame.pack(fill="x", padx=15, pady=5)

        self.use_custom_target_var = tk.BooleanVar(value=False)
        self.custom_target_checkbox = ttk.Checkbutton(
            custom_frame,
            text="Use custom target model name",
            variable=self.use_custom_target_var,
            command=self.toggle_custom_target_entry
        )
        self.custom_target_checkbox.pack(side="left", padx=5)

        self.custom_target_entry = ttk.Entry(custom_frame, width=30, state=tk.DISABLED)
        self.custom_target_entry.pack(side="left", padx=5)

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

    def toggle_custom_target_entry(self):
        """Enables or disables the custom target model entry based on the checkbox state."""
        if self.use_custom_target_var.get():
            self.custom_target_entry.config(state=tk.NORMAL)
        else:
            self.custom_target_entry.config(state=tk.DISABLED)
 
    def start_workflow(self):
        """Kicks off the complete workflow lifecycle from the UI thread."""
        self.is_cancelled_by_user = False
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.text_box.delete("1.0", tk.END)

        # Handle custom target model property update if checked
        if self.use_custom_target_var.get():
            custom_name = self.custom_target_entry.get().strip()
            messagebox.showinfo("Info", f"Custom target model name: {custom_name}, implementation TBD")

        # Redirect standard output so all print statements stream directly into the text box
        self.original_stdout = sys.stdout
        sys.stdout = StdoutRedirector(self.text_box)

        try:
            # 1. Pre-Pipeline Tasks (Unloads model)
            self.run_pre_pipeline_tasks()

            # 2. Kick off the core background training pipeline controller[cite: 3, 5]
            self.active_controller = training_service.apply_pipeline()
            self.poll_workflow()

        except Exception as e:
            sys.stdout = self.original_stdout
            self.text_box.insert(tk.END, f"\n[Error] Failed to start pipeline: {e}\n", "error_tag")
            self.status_label.config(text="Pipeline failed during launch.")
            self.start_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)

    def run_pre_pipeline_tasks(self):
        """Handles tasks to perform before the training cycle starts."""
        self.status_label.config(text="Preparing: Unloading inference model...")
        self.text_box.insert(tk.END, "=== PRE-PIPELINE: UNLOADING INFERENCE MODEL ===\n", "pipeline_tag")
        
        # Free up unified memory by unloading the active model before training begins
        inference_engine.unload_model()
        
        self.status_label.config(text="Running training pipeline...")
        self.text_box.insert(tk.END, "=== STARTING TRAINING PIPELINE ===\n", "pipeline_tag")

    def run_post_pipeline_tasks(self):
        """Handles cleanup and recovery tasks after a successful training cycle."""
        self.status_label.config(text="Finishing: Reloading inference model...")
        self.text_box.insert(tk.END, "\n=== POST-PIPELINE: RELOADING INFERENCE MODEL ===\n", "pipeline_tag")

        try:
            inference_engine.load_model()
            self.text_box.insert(tk.END, "[InferenceEngine] Model reloaded successfully.\n", "controller_tag")
        except Exception as e:
            self.text_box.insert(tk.END, f"[Error] Failed to reload model: {e}\n", "error_tag")
            messagebox.showerror("Error", f"Failed to load model:\n{e}")

        self.status_label.config(text="Pipeline completed successfully!")
        self.text_box.insert(tk.END, "=== PIPELINE COMPLETED SUCCESSFULLY ===\n", "pipeline_tag")

    def confirm_cancel(self):
        """Requests graceful pipeline halt after the current step finishes."""
        if not self.active_controller or not self.active_controller.is_alive():
            return

        response = messagebox.askyesno(
            "Confirm Stop",
            "This will let the current step finish and then safely stop the pipeline.\nDo you want to proceed?",
            icon="warning"
        )

        if response:
            self.is_cancelled_by_user = True
            self.status_label.config(text="Stopping after current step...")
            self.text_box.insert(tk.END, "\n[User Action] Stop requested. Waiting for current step to complete...\n", "error_tag")
            training_service.request_cancel()

    def poll_workflow(self):
        """Periodically checks if the master pipeline controller is still alive."""
        if not self.active_controller:
            return

        if self.active_controller.is_alive():
            self.after(200, self.poll_workflow)
        else:
            if self.original_stdout:
                sys.stdout = self.original_stdout

            self.start_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)

            if self.is_cancelled_by_user:
                self.status_label.config(text="Pipeline cancelled by user.")
                self.text_box.insert(tk.END, "\n=== PIPELINE ABORTED BY USER ===\n", "error_tag")
            elif self.active_controller.was_successful():
                # Execute Post-Pipeline tasks cleanly here
                self.run_post_pipeline_tasks()
            else:
                self.status_label.config(text="Pipeline failed.")
                self.text_box.insert(tk.END, "\n=== PIPELINE FAILED ===\n", "error_tag")
