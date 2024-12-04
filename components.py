from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView, Static

from utils import ALLOWED_FILTYPES, ICON, get_directory_contents


class MediaInfo(Vertical):
    """Displaying the media info"""

    def __init__(self, audio_title: str, artist_name: str, album: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_title = audio_title
        self.artist_name = artist_name
        self.album = album

    def compose(self) -> ComposeResult:
        yield Static(
            self.audio_title,
            id="media-title",
            classes="media-info-texts",
        )
        yield Static(
            self.artist_name,
            id="artist-name",
            classes="media-info-texts",
        )
        yield Static(
            self.album,
            id="album",
            classes="media-info-texts",
        )


class LabelItem(ListItem):
    """Custom Label as a ListItem."""

    def __init__(self, text: str, icon: str = "", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label_text = text
        self.icon = icon
        self.label = Label(self.icon + self.label_text)

    def compose(self) -> ComposeResult:
        """Load the text for the item."""
        yield self.label


class ControlButtons(Horizontal):
    """A container for the control buttons"""

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


class FileExplorer(ListView):
    """The album cover for the current media"""

    def __init__(self, title: str, player: Widget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = title
        self.path = Path.cwd()
        self.player = player
        self.classes = "file-explorer"

    async def on_mount(self) -> None:
        self.border_title = self.title
        await self.populate(self.path)

    async def populate(self, directory: Path):
        """Populate the ListView with files and directories"""
        self.append(LabelItem("../", icon=ICON["directory"]))
        try:
            # Lazy load directory content
            children = get_directory_contents(directory, self)
            for chunk in range(0, len(children), 10):
                for child in children[chunk : chunk + 10]:
                    if child.is_dir():
                        icon = ICON["directory"]
                    else:
                        icon = (
                            ICON["audio"]
                            if child.suffix in ALLOWED_FILTYPES
                            else ICON["document"]
                        )
                    self.append(LabelItem(child.name, icon=icon))
        except Exception as e:
            self.notify(f"Error loading directory: {e}")

    @on(ListView.Selected)
    async def selected(self, event: ListView.Selected):
        """Handle item selection."""
        selected_path = self.path.joinpath(event.item.label_text)

        if Path.is_dir(selected_path):
            if self.index == 0:
                self.path = Path(self.path).resolve().parent
            elif Path.is_dir(selected_path):
                self.path = selected_path

            await self.clear()
            self.notify(event.item.label_text)
            await self.populate(self.path)
            self.focus()
            return

        if Path(selected_path).suffix not in ALLOWED_FILTYPES:
            return

        if not self.player.playing_song or self.player.playing_song != selected_path:
            self.player.play_song(selected_path)
            return

        self.player.toggle_play_state()
