# ui_theme.py
import tkinter as tk
from tkinter import ttk

# --- GLOBAL DESIGN SYSTEM CONSTANTS ---
APP_FONT_FAMILY = "Helvetica"
APP_FONT_SIZE = 12
APP_HEADER_FONT_SIZE = 13

EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE = 12

# Light & Crisp Color Palette (Soft off-white / light blue-gray theme)
BG_APP = "#eef2f5"           # Main app background (soft light gray-blue)
BG_PANEL = "#ffffff"         # Clean white panels and notebook tabs
BG_INPUT = "#000000"         # Pure black for edit windows as requested
FG_DARK = "#222222"          # Dark, highly readable text for light areas
FG_INPUT = "#00ff66"         # Bright neon-on-black or crisp white text inside the black edit boxes
FG_MUTED = "#666666"         # Muted gray for inactive states

# High-contrast interactive buttons (e.g., crisp blue accent to stand out against light panels)
BTN_BG = "#0066cc"           
BTN_FG = "#ffffff"           
BTN_ACTIVE = "#0052a3"       

# Log Output / Console Theme Colors
LOG_BG = "#1e1e1e"           # Dark background for execution/log windows
LOG_FG_DEFAULT = "#00ff00"   # Classic green for standard output/commands
LOG_FG_PIPELINE = "#ffcc00"  # Gold/Yellow for [PIPELINE] milestones
LOG_FG_CONTROLLER = "#00bcd4"# Cyan/Blue for [ProcessController] tracking logs
LOG_FG_ERROR = "#ff5555"     # Red for errors and failures


def apply_global_theme(root):
    """Initializes and applies the global ttk theme across the application,
    featuring a bright, clean background with high-contrast buttons and pure black edit boxes.
    """
    style = ttk.Style(root)
    style.theme_use('clam')

    # Base ttk fallback - light background with dark text
    style.configure('.', 
                    font=(APP_FONT_FAMILY, APP_FONT_SIZE), 
                    background=BG_PANEL, 
                    foreground=FG_DARK)

    # Global Button Styling - designed to pop nicely against the light background
    style.configure('TButton', 
                    font=(APP_FONT_FAMILY, APP_FONT_SIZE, 'bold'),
                    padding=8,
                    relief='flat',
                    background=BTN_BG,
                    foreground=BTN_FG)
    style.map('TButton',
              background=[('active', BTN_ACTIVE), ('pressed', '#003d7a')],
              foreground=[('active', '#ffffff'), ('pressed', '#ffffff')])

    # Notebook & Tab Styling
    style.configure('TNotebook', background=BG_APP, borderwidth=0)
    style.configure('TNotebook.Tab', 
                    font=(APP_FONT_FAMILY, APP_FONT_SIZE, 'bold'), 
                    padding=[14, 10],
                    background='#d0dbe5',
                    foreground=FG_MUTED)
    style.map('TNotebook.Tab',
              background=[('selected', BG_PANEL)],
              foreground=[('selected', FG_DARK)])

    # Label & Frame Adjustments
    style.configure('TLabel', background=BG_PANEL, foreground=FG_DARK)
    style.configure('TFrame', background=BG_PANEL)
    style.configure('Labelframe', background=BG_PANEL, foreground=FG_DARK)
    style.configure('Labelframe.Label', background=BG_PANEL, foreground=FG_DARK, font=(APP_FONT_FAMILY, APP_FONT_SIZE, 'bold'))


def create_styled_text(parent, height=10, width=40):
    """Factory function for standard text edit windows.
    Enforces a pure black background with contrasting bright text and a larger font size.
    """
    return tk.Text(
        parent,
        font=(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE),
        bg=BG_INPUT,                 # Pure black background
        fg="#ffffff",                # Crisp white text for optimal readability on black
        insertbackground="#00ffcc",  # High-visibility cyan cursor
        selectbackground="#005fb8",  # Clean selection highlight
        selectforeground="#ffffff",
        relief='flat',
        bd=6,
        wrap='word',
        height=height,
        width=width
    )