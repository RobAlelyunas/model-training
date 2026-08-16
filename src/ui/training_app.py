import tkinter as tk
from tkinter import messagebox, ttk
from src.ui.apply_tab import ApplyTab
from src.ui.data_tab import DataTab
from src.ui.train_tab import TrainTab
from src.ui.setup_tab import SetupTab
from src.ui.ui_theme import apply_global_theme
from src.ui.ui_helpers import ensure_setup_complete

class TrainingApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("LLM Training Manager")
        self.geometry("950x700")
        self.minsize(750, 550)

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
        """Enforces the setup complete guard by snapping back to Setup first, then alerting."""
        try:
            selected_tab_index = self.notebook.index(self.notebook.select())
        except Exception:
            return

        # Setup tab (index 0) is always allowed
        if selected_tab_index == 0:
            self.current_tab_index = 0
            return

        # Check if mandatory setup requirements are met
        if not ensure_setup_complete():
            # 1. Snap back to Setup immediately first
            self.notebook.select(0)
            self.current_tab_index = 0
            
            # 2. Then show the warning message popup centered on the app window
            messagebox.showwarning(
                "Setup Required",
                "Please configure your models, dataset, and chat template in the Setup tab before continuing.",
                parent=self
            )
        else:
            self.current_tab_index = selected_tab_index

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