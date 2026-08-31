from src.ui.help.help_dialog import HelpDialog

class DataHelpDialog(HelpDialog):
    def __init__(self, parent):
        # Initialize the base modal dialog with a custom title and size
        super().__init__(parent, title="Dataset Editor Help")

        # Populate the help content
        self._populate_content()
        
        # Lock text widget to read-only
        self.finalize_content()

    def _populate_content(self):
        self.insert_heading_1("Dataset Editor Help")
        
        self.insert_paragraph(
"""On this tab you can directly edit the dataset.  \
Your dataset should contain at least one record."""
        )