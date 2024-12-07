
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button


class ControlButtons(Horizontal):
    """A container for the control buttons."""

    shuffle_button = Button("shuffle", id="shuffle", classes="control-buttons")
    prev_button = Button("prev", id="prev", classes="control-buttons")
    play_button = Button("play", id="play", classes="control-buttons")
    next_button = Button("next", id="next", classes="control-buttons")
    loop_button = Button("loop", id="loop", classes="control-buttons")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Create the control buttons."""
        yield self.shuffle_button
        yield self.prev_button
        yield self.play_button
        yield self.next_button
        yield self.loop_button
