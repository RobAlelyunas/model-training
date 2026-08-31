import tkinter as tk
from tkinter import messagebox, ttk
from src.core.global_state import get_property
from src.core.storage import get_references_dir
from src.ui.apply_tab import ApplyTab
from src.ui.data_tab import DataTab
from src.ui.train_tab import TrainTab
from src.ui.setup_tab import SetupTab
from src.ui.ui_theme import apply_global_theme
from src.ui.help.splash_screen import SplashScreen
from src.ui.help.setup_tab_help import SetupHelpDialog
from src.ui.help.train_tab_help import TrainHelpDialog
from src.ui.help.apply_tab_help import ApplyHelpDialog
from src.ui.help.data_tab_help import DataHelpDialog

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

        self.train_tab = TrainTab(self.notebook)
        self.notebook.add(self.train_tab, text="Interactive Training")

        self.apply_tab = ApplyTab(self.notebook)
        self.notebook.add(self.apply_tab, text="Apply Training")

        self.data_tab = DataTab(self.notebook)
        self.notebook.add(self.data_tab, text="Dataset Editor")

        self.setup_tab = SetupTab(self.notebook)
        self.notebook.add(self.setup_tab, text="Setup")

        # Check startup property and trigger splash screen if enabled
        if get_property("show_splash_on_startup"):
            self.after(100, lambda: SplashScreen(self))

    def show_context_help(self):
        try:
            current_tab_widget = self.notebook.nametowidget(self.notebook.select())
        except Exception:
            current_tab_widget = None

        # Map each tab instance to its specific help content
        if current_tab_widget == self.setup_tab:
            SetupHelpDialog(self)
        elif current_tab_widget == self.apply_tab:
            ApplyHelpDialog(self)
        elif current_tab_widget == self.data_tab:
            DataHelpDialog(self)
        elif current_tab_widget == self.train_tab:
            TrainHelpDialog(self)
        else:
            SplashScreen(self)