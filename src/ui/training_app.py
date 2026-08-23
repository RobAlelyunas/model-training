import tkinter as tk
from tkinter import messagebox, ttk
from src.core.global_state import get_property
from src.core.storage import get_references_dir
from src.ui.apply_tab import ApplyTab
from src.ui.data_tab import DataTab
from src.ui.train_tab import TrainTab
from src.ui.setup_tab import SetupTab
from src.ui.ui_theme import apply_global_theme

class TrainingApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Interactive Model Training")
        self.geometry("950x700")
        self.minsize(750, 550)
        app_icon = tk.PhotoImage(file=get_references_dir() / "icon.png")
        self.iconphoto(True,app_icon)
        # Apply the custom theme to the entire application[cite: 4]
        apply_global_theme(self)

        header_frame = ttk.Frame(self)
        header_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.notebook = ttk.Notebook(header_frame)
        self.notebook.pack(expand=True, fill="both")

        self.global_help_label = ttk.Label(
            header_frame, text="Help", font=("Helvetica", 11, "bold"), foreground="#007acc", cursor="hand2"
        )
        self.global_help_label.place(relx=1.0, x=-15, rely=0.02, anchor="ne")
        self.global_help_label.bind("<Button-1>", lambda e: self.show_context_help())

        # Add the Setup Tab first (Index 0)
        self.setup_tab = SetupTab(self.notebook)
        self.notebook.add(self.setup_tab, text="Setup")

        self.train_tab = TrainTab(self.notebook)
        self.notebook.add(self.train_tab, text="Interactive Training")

        self.apply_tab = ApplyTab(self.notebook)
        self.notebook.add(self.apply_tab, text="Apply Training")

        self.data_tab = DataTab(self.notebook)
        self.notebook.add(self.data_tab, text="Dataset Editor")

        # Track current tab index for guard rollbacks
        self.current_tab_index = 0
        
        # Bind the notebook tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """Guard for tab changes"""
        selected_tab_index = self.notebook.index(self.notebook.select())
        source_model = get_property("source_model")
        target_model = get_property("target_model")
        dataset = get_property("dataset")
        chat_template = get_property("chat_template")
        if selected_tab_index == 0:
            # Setup tab (index 0)
            self.current_tab_index = 0
        elif selected_tab_index == 1:
            # Interactive Training tab
            if not target_model or not dataset or not chat_template:
                self.notebook.select(0)
                self.current_tab_index = 0
                messagebox.showinfo(
                    title="Setup Required",
                    message="Interactive training requires a selected target model, dataset, and chat template",
                    parent=self)
            else:
                self.current_tab_index = 1
        elif selected_tab_index == 2:
            # Apply Training tab
            if not source_model or not target_model or not dataset or not chat_template:
                self.notebook.select(0)
                self.current_tab_index = 0
                messagebox.showinfo(
                    title="Setup Required",
                    message="Apply training requires a selected source model, target model, dataset, and chat template",
                    parent=self)
            else:
                self.current_tab_index = 2
        elif selected_tab_index == 3:
            # Dataset editor tab
            if not dataset:
                self.notebook.select(0)
                self.current_tab_index = 0
                messagebox.showinfo(
                    title="Setup Required",
                    message="Dataset editor requires a selected dataset",
                    parent=self)
            else:
                self.current_tab_index = 3
    

    def show_context_help(self):
        """Determines the active tab and displays the corresponding context-dependent help message."""
        try:
            current_tab_widget = self.notebook.nametowidget(self.notebook.select())
        except Exception:
            current_tab_widget = None

        # Map each tab instance to its specific help content
        if current_tab_widget == self.setup_tab:
            messagebox.showinfo(
                "Setup Help",
                "Configure your source model, target model, dataset, and chat template here before using other tabs.",
                parent=self
            )
        elif current_tab_widget == self.apply_tab:
            messagebox.showinfo(
                "Apply Training Help",
                "This is the placeholder for Apply Training help documentation.",
                parent=self
            )
        elif current_tab_widget == self.data_tab:
            messagebox.showinfo(
                "Dataset Help",
                "This is the placeholder for Dataset Editor help documentation.",
                parent=self
            )
        elif current_tab_widget == self.train_tab:
            messagebox.showinfo(
                "Train Model Help",
                "The Train tab allows you to train your model with the configured dataset.\n\n"
                "will be saved instead of the model's original response.",
                parent=self
            )
        else:
            messagebox.showinfo(
                "Help",
                "This is the placeholder for general application help.",
                parent=self
            )