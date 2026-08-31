from src.ui.help.help_dialog import HelpDialog

class ApplyHelpDialog(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal dialog with a custom title and size
        super().__init__(parent, title="Apply Training Help")

        # Populate the help content
        self._populate_content()
        
        # Lock text widget to read-only
        self.finalize_content()

    def _populate_content(self):
        self.insert_heading_1("Apply Training Help")

        self.insert_heading_1("Basics") 
        self.insert_paragraph(
"""On this tab you will apply your dataset to the source model to produce \
an updated target model.  First, make sure you've selected the desired source \
model, target model, and dataset on the Setup tab.  When you press the 'Run' \
button, you will see a stream of output as the system performs several steps. \
First, the dataset will be reformatted to fit the model training input format \
and placed in a special directory.  Then that dataset will be applied to the source model to create a Low Resolution \
Adapter.  This adapter will then be fused back to the source model to create a fused model. \
Usually, a chat model is then added to the fused model. The fused model might then \
be quantized, which can reduce the size. finally it \
is copied to replace the target model and loaded as the new inference engine \
for the Interactive Training tab. """)

        self.insert_heading_1("Hyperparameters") 
        self.insert_paragraph(
"""The hyperparamters govern the training process.  If you are new to training \
models and don't unerstand these, use the 'Auto Set' button and it will choose \
values for you based on the source model, target model, and dataset you have \
chose on the Setup tab.  If you are working with a previously quantized source \
model, you won't want to perform quantization, which is a process that shrinks \
the model size by converting the 16 bit weights to fewer bits, such as 4. """)