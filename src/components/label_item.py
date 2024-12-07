
from textual.app import ComposeResult
from textual.widgets import Label, ListItem


class LabelItem(ListItem):
    """Custom Label as a ListItem."""

    def __init__(self, text: str, icon: str = "", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label_text = text
        self.icon = icon
        self.label = Label(self.icon + self.label_text)
        self.initialized = True

    def compose(self) -> ComposeResult:
        """Load the text for the item."""
        yield self.label
