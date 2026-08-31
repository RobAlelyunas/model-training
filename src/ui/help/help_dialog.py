import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path
from src.core.logging import log

class HelpDialog(tk.Toplevel):
    def __init__(self, parent, title="Dialog", width=750, height=630, images_dir=None):
        super().__init__(parent)
        
        # Modal window setup
        self.transient(parent)
        self.grab_set()
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Center the modal relative to parent
        self.update_idletasks()
        p_x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        p_y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{max(0, p_x)}+{max(0, p_y - 20)}")

        # Keep references to prevent garbage collection of images
        self.image_refs = []
        self.images_dir = images_dir or Path(__name__).parent / "assets"

        # Main layout container with padding
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(expand=True, fill="both")

        # Scrollable text area container
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(expand=True, fill="both", pady=(0, 15))

        self.text_widget = tk.Text(
            canvas_frame, 
            wrap="word", 
            relief="flat", 
            bg=self.cget("bg"),
            highlightthickness=0,
            padx=10,
            pady=10
        )
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)

        self.text_widget.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        # Configure typography tags
        self.text_widget.tag_configure("h1", font=("Helvetica", 16, "bold"), spacing1=14, spacing2=6)
        self.text_widget.tag_configure("h2", font=("Helvetica", 13, "bold"), spacing1=10, spacing2=4)
        self.text_widget.tag_configure("body", font=("Helvetica", 11), spacing1=4, spacing2=4)
        self.text_widget.tag_configure("center", justify="center")

        # Bottom control bar container (Children can add widgets via self.bottom_bar)
        self.bottom_bar = ttk.Frame(main_frame)
        self.bottom_bar.pack(fill="x", side="bottom")

        # Default Close Button (Right side)
        close_btn = ttk.Button(self.bottom_bar, text="Close", command=self.close_dialog, width=12)
        close_btn.pack(side="right")
        
        self.protocol("WM_DELETE_WINDOW", self.close_dialog)

    # =========================================================================
    # PUBLIC CONTENT-BUILDING API METHODS
    # =========================================================================

    def insert_heading_1(self, text):
        """Inserts a Level 1 primary section heading."""
        self.text_widget.insert("end", f"{text}\n", "h1")

    def insert_heading_2(self, text):
        """Inserts a Level 2 subsection heading."""
        self.text_widget.insert("end", f"{text}\n", "h2")

    def insert_paragraph(self, text):
        """Inserts a block of body text."""
        self.text_widget.insert("end", f"{text}\n\n", "body")

    def insert_image(self, filename, width=540):
        """Inserts an image centered inline, scaling height automatically based on aspect ratio."""
        img_path = Path(filename)
        if not img_path.is_absolute():
            img_path = self.images_dir / filename

        if img_path.exists():
            try:
                pil_img = Image.open(img_path)
                w_percent = width / float(pil_img.size[0])
                h_size = int(float(pil_img.size[1]) * float(w_percent))
                pil_img = pil_img.resize((width, h_size), Image.Resampling.LANCZOS)
                
                tk_img = ImageTk.PhotoImage(pil_img)
                self.image_refs.append(tk_img)  
                
                self.text_widget.insert("end", "\n", "body")
                image_index = self.text_widget.index("end-1c")
                self.text_widget.image_create("end", image=tk_img)
                self.text_widget.tag_add("center", image_index, "end")
                self.text_widget.insert("end", "\n\n", "body")
            except Exception as e:
                log("ScrollableModalDialog", f"Could not load image {filename}: {e}")
        else:
            log("ScrollableModalDialog", f"Image path not found: {img_path}")

    def finalize_content(self):
        """Call this at the end of child __init__ to lock the text box to read-only."""
        self.text_widget.configure(state="disabled")

    def close_dialog(self):
        self.grab_release()
        self.destroy()