import tkinter as tk
from tkinter import ttk

from src.ui.help.help_dialog import HelpDialog
from src.core.global_state import get_property, set_property
from src.core.storage import get_references_dir

class SplashScreen(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal window with custom title/size
        super().__init__(parent, title="Interactive Model Training", width=600, height=200)
        
        # Add the "Show at startup" checkbox to the left side of the shared bottom bar
        self.show_startup_var = tk.BooleanVar(value=get_property("show_splash_on_startup"))
        self.startup_checkbox = ttk.Checkbutton(
            self.bottom_bar, 
            text="Show this at startup", 
            variable=self.show_startup_var,
            command=self._on_checkbox_toggled
        )
        self.startup_checkbox.pack(side="left")

        # Populate content using the inherited methods
        self._populate_content()
        
        # Lock text widget to read-only
        self.finalize_content()

    def _populate_content(self):
        """Define splash screen text and figures."""
        self.insert_heading_1("Welcome to Interactive Model Training!")
        self.insert_paragraph(
"""This application allows you to train and customize language models interactively.
For detailed guidance, please refer to the help sections available in each tab.""")

        self.insert_image(get_references_dir() / "grimace.png", width=100)
    def _on_checkbox_toggled(self):
        state = self.show_startup_var.get()
        set_property("show_splash_on_startup", state)