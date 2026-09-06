from src.core.storage import get_references_dir
from src.ui.help.help_dialog import HelpDialog

class TrainHelpDialog(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal dialog with a custom title and size
        super().__init__(parent, title="Interactive Training Help")

        # Populate the help content
        self._populate_content()
        
        # Lock text widget to read-only
        self.finalize_content()

    def _populate_content(self):
        self.insert_heading_1("Interactive Model Training")     
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

        self.insert_image(get_references_dir() / "allhuman.png", width=500)  

        self.insert_heading_2("Chat Models are Friendly")
        self.insert_paragraph(
"""Most chat models are friendly and helpful. They try to answer questions faithfully, \
and they follow strict safety guidelines. Your model doesn't have \
to be like this. For example, it doesn't have to be friendly, it doesn't have to tell the \
truth, and so on.   This is your model, whatever you think is interesting, do it!""")

        self.insert_heading_2("Interactive Training")      
        self.insert_paragraph(
"""Create your dataset on this tab by interacting with your current version of the \
target model.
1. New Prompt - Type a prompt or select a random prompt.
2. Generate Answer -  Let the current target model produce an answer.
3. Refine Answer - If you don't like the answer, edit and improve it.
4. Add to Training Data - if you changed it, add the prompt and answer to your dataset.
5. Apply Training - When you have enough new records in your dataset, go to the \
apply training tab and apply the dataset to create a new target model.
""")
        self.insert_heading_1("Datasets")     
        self.insert_image(get_references_dir() / "datasetplus.png", width=500)  
        self.insert_heading_2("A Dataset")
        self.insert_paragraph(
"""A dataset is a simple file of prompts and answers - prompts that might be asked, and answers that you \
would like to see. The dataset is what we use to train a model. It has the prompts and answers that you \
want. Using a dataset to train a model is often called Supervised Fine Tuning (SFT), and it's what you \
are about to do.""")
        
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

        self.insert_image(get_references_dir() / "grimace.png", width=100)  
 
