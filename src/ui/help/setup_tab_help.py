from src.ui.help.help_dialog import HelpDialog

class SetupHelpDialog(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal dialog with a custom title and size
        super().__init__(parent, title="Setup Help")

        # Populate the help content
        self._populate_content()
        
        # Lock text widget to read-only
        self.finalize_content()

    def _populate_content(self):
        """Define setup help documentation, headings, and optional images."""
        self.insert_heading_1("Setup Help")
        self.insert_heading_2("1. Choose Source Model")
        self.insert_paragraph(
"""The source model is the model that will have the training data applied to it. It might be \
a base model such as Meta_Llama_8_3B.  The source models are chosen from the models/sources directory \
When you first start, then are no source models available.  This is because these models are \
large, as large as 16 GB, and you will need to download the source you want to use \
separarely from this application.  A button is provided that lets you download a 6 GB model \
that has already been prepared and is available publicly on Hugging Face. You can \
use different models than this, and download it yourself to the models/sources directory \
to make it available to be chosen here. Note that if your Mac has only 12 GB of memory, then \
a model of size 10 GB or so can be handled by your system but not much larger. The model \
size should be less than your available memory.  Larger models are more accurate, so try \
different things. The starter model has been quantized, which means the 16 bit model weights \
have been averaged down to 4 bits each, which makes the model much smaller but less \
accurate. You must choose a source model to continue.
 """)
        self.insert_heading_2("2. Choose Target Model")
        self.insert_paragraph(
"""The target model is a soure model after it has been trained with your dataset.  At first \
when you haven't trained anything yet, you still need a target model to use for \
interactive training on the Interactive Training tab, so what you can do is use the \
button to copy the current source model and use it untrained as the target model \
in your first iteration.  This means the model will produce some lousy results, its \
untrained, but that will be interesting in terms of understanding your source model. \
You must choose a target model to continue. When you are satisfied with the training, \
go to the models/targets directory shown to get your target model and release it or \
use it for your chat engine.
 """)
        self.insert_heading_2("3. Choose Dataset")
        self.insert_paragraph(
"""The dataset is a working file where your training data accumulates.  Since you retrain the \
source model every time, the dataset file is the only record of your gradual \
improvement of the target model.  This will accumulate over iterations, you can \
start with a new dataset with a single record by using the button.  You can also \
select and test some of the prepared datasets that come with the project that might \
be interesting.
 """)
        self.insert_heading_2("3. Chat Template")
        self.insert_paragraph(
"""The dataset is a working file where your training data accumulates.  Since you retrain the \
source model every time, the dataset file is the only record of your gradual \
improvement of the target model.  This will accumulate over iterations, you can \
start with a new dataset with a single record by using the button.  You can also \
select and test some of the prepared datasets that come with the project that might \
be interesting.
 """)
        
        