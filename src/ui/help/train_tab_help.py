from src.core.storage import get_references_dir
from src.ui.help.help_dialog import HelpDialog

class TrainHelpDialog(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal dialog with a custom title and size
        super().__init__(parent, title="Setup Help")

        # Populate the help content
        self._populate_content()
        
        # Lock text widget to read-only
        self.finalize_content()

    def _populate_content(self):
        """Define setup help documentation, headings, and optional images."""
        self.insert_heading_1("Interactive Training Help")
        
        self.insert_paragraph(
"""Create your dataset on this tab by interacting with your current version of the \
target model.
""")
        self.insert_paragraph(
"""1. New Prompt - Type a prompt or select a random prompt.
2. Generate Answer -  Let the current target model produce an answer.
3. Refine Answer - If you don't like the answer, edit and improve it.
4. Add to Training Data - if you changed it, add the prompt and answer to your dataset.
5. Apply Training - When you have enough new records in your dataset, go to the \
apply training tab and use the larger dataset to create a new target model.
""")

        self.insert_image(get_references_dir() / "interactive.png",width=650)
