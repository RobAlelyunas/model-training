import json
import random
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from src.global_state import get_property
from src.services.inference_engine import inference_engine
from src.ui.ui_theme import create_styled_text
from src.global_state import register_state_change_handler
from src.global_state import set_property

class TrainTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_notebook = parent
        self.prompts_file = Path("resources/prompts.txt")
        self.working_dataset_path = Path(get_property("dataset_path"))
        self.target_model = get_property("target_model")
        self.target_model_path = Path(f"models/targets/{self.target_model}")
        self.current_prompt = ""
        self.current_response = ""
        self.create_widgets()
        register_state_change_handler(self.global_state_changed)

    def global_state_changed(self):
        """Reloads cached global properties when state changes."""
        self.working_dataset_path = Path(get_property("dataset_path"))
        self.target_model = get_property("target_model")
        self.target_model_path = Path(f"models/targets/{self.target_model}")

    def create_widgets(self):
        # Main container
        editor_container = ttk.Frame(self)
        editor_container.pack(expand=True, fill="both", padx=15, pady=15)
        editor_container.rowconfigure(0, weight=1) # Top: Prompt section (narrower)
        editor_container.rowconfigure(1, weight=4) # Bottom: Tabbed interface for responses
        editor_container.columnconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # TOP SECTION: Prompt (Narrow, e.g. 4 lines high, with Select Random button)
        # ---------------------------------------------------------------------
        prompt_frame = ttk.Frame(editor_container)
        prompt_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        prompt_frame.rowconfigure(1, weight=1)
        prompt_frame.columnconfigure(0, weight=1)

        prompt_header_frame = ttk.Frame(prompt_frame)
        prompt_header_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        prompt_header_frame.columnconfigure(0, weight=1)

        ttk.Label(prompt_header_frame, text="Prompt (Type your own or load a random one)").pack(side="left")
        self.random_prompt_button = ttk.Button(
            prompt_header_frame, text="Select Random Prompt", command=self.on_random_prompt_clicked
        )
        self.random_prompt_button.pack(side="right")

        self.prompt_text = create_styled_text(prompt_frame, height=4)
        self.prompt_text.grid(row=1, column=0, sticky="nsew", padx=2, pady=(2, 0))
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky="ns", pady=(2, 0))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)

        # ---------------------------------------------------------------------
        # BOTTOM SECTION: Notebook with two tabs (Generated Answer vs Alternative Answer)
        # ---------------------------------------------------------------------
        self.bottom_notebook = ttk.Notebook(editor_container)
        self.bottom_notebook.grid(row=1, column=0, sticky="nsew")

        # --- Tab 1: Model Response ---
        response_tab = ttk.Frame(self.bottom_notebook)
        response_tab.rowconfigure(1, weight=1)
        response_tab.columnconfigure(0, weight=1)

        response_header_frame = ttk.Frame(response_tab)
        response_header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        response_header_frame.columnconfigure(0, weight=1)

        ttk.Label(response_header_frame, text=f"Model Response ({self.target_model})").pack(side="left")
        
        response_btn_subframe = ttk.Frame(response_header_frame)
        response_btn_subframe.pack(side="right")

        self.generate_button = ttk.Button(
            response_btn_subframe, text="Generate Answer", command=self.on_generate_clicked
        )
        self.generate_button.pack(side="left")

        self.response_text = create_styled_text(response_tab, height=12)
        self.response_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.response_text.configure(state="disabled")
        
        response_scroll = ttk.Scrollbar(response_tab, orient="vertical", command=self.response_text.yview)
        response_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 5))
        self.response_text.configure(yscrollcommand=response_scroll.set)

        # --- Tab 2: Alternative Answer ---
        alt_tab = ttk.Frame(self.bottom_notebook)
        alt_tab.rowconfigure(1, weight=1)
        alt_tab.columnconfigure(0, weight=1)

        alt_header_frame = ttk.Frame(alt_tab)
        alt_header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        alt_header_frame.columnconfigure(0, weight=1)

        ttk.Label(alt_header_frame, text="Alternative Answer (Optional override)").pack(side="left")
        
        self.add_button = ttk.Button(
            alt_header_frame, text="Add Training Data", command=self.on_add_clicked
        )
        self.add_button.pack(side="right")

        self.alt_text = create_styled_text(alt_tab, height=12)
        self.alt_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        
        alt_scroll = ttk.Scrollbar(alt_tab, orient="vertical", command=self.alt_text.yview)
        alt_scroll.grid(row=1, column=1, sticky="ns", pady=(0, 5))
        self.alt_text.configure(yscrollcommand=alt_scroll.set)

        # Add tabs to the bottom notebook
        self.bottom_notebook.add(response_tab, text="Generated Answer")
        self.bottom_notebook.add(alt_tab, text="Alternative Answer")

    
    def load_random_prompt_text(self):
        """Picks a random prompt from resources/prompts.txt and populates the prompt box without auto-generating."""
        if not self.prompts_file.exists():
            messagebox.showwarning("Warning", f"Prompt file not found at {self.prompts_file}")
            return
        
        try:
            with open(self.prompts_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                messagebox.showwarning("Warning", "The prompts.txt file is empty.")
                return
            
            chosen_prompt = random.choice(lines)
            
            # Populate prompt box
            self.prompt_text.delete("1.0", "end")
            self.prompt_text.insert("1.0", chosen_prompt)

            # Clear response and alternative text boxes for the new cycle
            self.response_text.configure(state="normal")
            self.response_text.delete("1.0", "end")
            self.response_text.insert("1.0", "Click 'Generate Answer' to query the model.")
            self.response_text.configure(state="disabled")

            self.alt_text.delete("1.0", "end")
            self.current_response = ""

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load random prompt:\n{e}")

    def on_random_prompt_clicked(self):
        """Button action to fetch and display a random prompt."""
        self.load_random_prompt_text()

    def on_generate_clicked(self):
        """User-triggered action to run inference using whatever is currently in the prompt box."""
        if not inference_engine.is_model_loaded():
            messagebox.showerror("Warning", "Model is not loaded.")
            return

        prompt_content = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt_content:
            messagebox.showwarning("Warning", "Prompt box is empty. Please enter or load a prompt first.")
            return

        self.current_prompt = prompt_content

        # Immediately show loading state in response box & force watch cursor
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", "Loading...")
        self.response_text.configure(state="disabled")
        
        self.config(cursor="watch")
        self.update()

        try:
            self.current_response = inference_engine.generate_chat_response(self.current_prompt)
        except Exception as e:
            print(f"Inference error: {e}")
            self.current_response = f"[Error during generation: {e}]"
        finally:
            self.config(cursor="")
            self.update()

        # Update response box with final output
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", self.current_response)
        self.response_text.configure(state="disabled")

    def on_add_clicked(self):
        """Saves the prompt and either the custom alternative answer or model response to dataset."""
        prompt_content = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt_content:
            messagebox.showwarning("Warning", "No active prompt available to save.")
            return

        alternative_answer = self.alt_text.get("1.0", "end-1c").strip()
        answer_to_save = alternative_answer if alternative_answer else self.current_response

        if not answer_to_save:
            messagebox.showwarning("Warning", "No response or alternative answer available to save. Please generate or type an answer.")
            return

        record = {
            "prompt": prompt_content,
            "completion": answer_to_save
        }

        try:
            self.working_dataset_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.working_dataset_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"Successfully added curated record to {self.working_dataset_path}")
            set_property("dataset_version", get_property("dataset_version") + 1)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to append record to dataset:\n{e}")
            return

        # Automatically advance to the next random prompt after adding
        self.load_random_prompt_text()