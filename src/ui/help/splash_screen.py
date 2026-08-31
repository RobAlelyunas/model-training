import tkinter as tk
from tkinter import ttk

from src.ui.help.help_dialog import HelpDialog
from src.core.global_state import get_property, set_property
from src.core.storage import get_references_dir

class SplashScreen(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal window with custom title/size
        super().__init__(parent, title="Startup Help")
        
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
        self.insert_heading_1("Interactive Model Training")     
        self.insert_image(get_references_dir() / "allhuman.png", width=650)  
        self.insert_heading_2("Raw Models")
        self.insert_paragraph(
"""The raw model costs billions of dollars to develop and contains all of our \
language. You will add behavior to that and get a chat model.  You'll get the raw \
model for free, from a company like Meta (thank you!) and then create a dataset to \
to train that model and make it your own.""")

        self.insert_heading_2("Raw Models look Stupid")
        self.insert_paragraph(
"""A raw model doesn't chat, or answer questions. It just acts stupid, taking whatever \
prompt you give it and coming up with what someone might say to continue that train \
of thought.  It looks stupid.  You'll see that when you first start working with your \
raw model. To get it to have a personality, or behave, you have \
to train that into the model with Supervised Fine Tuning (SFT) using your own custom dataset.""")

        self.insert_heading_2("Chat Models are Friendly")
        self.insert_paragraph(
"""Most chat models are friendly and helpful. They try to answer questions faithfully, \
and they follow strict safety guidelines. Your model doesn't have \
to be like this. For example, it doesn't have to be friendly, it doesn't have to tell the \
truth, and so on.   This is your model, whatever you think is interesting, do it!""")

        self.insert_image(get_references_dir() / "prompting.png", width=300)
        self.insert_heading_2("Prompting is Pretending")
        self.insert_paragraph(
"""How is this different from prompting?  In prompting, we take a highly trained chat model and tell \
it to add some behavior. \
No matter what you tell it, it is still trying to be helpful and have a pleasant personality and follow \
guidelines, but it has been told to pretend to be otherwise. This is a subtle but important distinction. \
When you train your own model, it's not pretending, it can't be \
altered, it can't be circumvented, and it's permanent.  Try it out both ways, and you will see the \
difference. Sometimes prompting is better, sometimes you just want to train your own.""")

        self.insert_heading_1("Datasets")     
        self.insert_image(get_references_dir() / "datasetplus.png", width=500)  
        self.insert_heading_2("A Dataset")
        self.insert_paragraph(
"""A dataset is a simple file of prompts and answers - prompts that might be asked, and answers that you \
would like to see. The dataset is what we use to train a model. It has the prompts and answers that you \
want. Using a dataset to train a model is often called Supervised Fine Tuning (SFT), and it's what you \
are about to do.""")

        self.insert_heading_2("Creating a Dataset")
        self.insert_paragraph(
"""You can create a dataset with interactive training like this:

  1. Go to the Train tab.
  2. Type or generate a new prompt.
  3. Generate an answer using the current target model.
  4. Improve or edit the answer until it looks like what you want.
  5. Add the prompt and answer pair to your dataset.
  6. Repeat this process until you have enough new records in your dataset.
  7. Go to the apply tab, and apply your dataset to create a new target model.
  8. Wait for the pipeline to build the new target model.
  9. Generate the new target model to see if your dataset is working.
  
  Alternatively, you can directly edit or create dataset entries in the dataset editor tab.""")
        
        self.insert_heading_1("Setup")     
        self.insert_heading_2("Initial Setup")
        self.insert_paragraph(
"""Before getting started, on the setup tab you need to setup a source model, \
a target model, and a working dataset file.""")
        
        self.insert_image(get_references_dir() / "grimace.png", width=400)  

    def _on_checkbox_toggled(self):
        state = self.show_startup_var.get()
        set_property("show_splash_on_startup", state)