from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView, Static

from utils import (ALLOWED_AUDIO_EXTENSIONS, ICON, get_directory_contents,
                   get_metadata, is_valid_media)


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
    """A minimal file explorer."""

    BINDINGS = [
        ("a", "add_to_playlist", "Add to the playlist"),
    ]

    def __init__(self, player: Widget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.path = Path.cwd()
        self.player = player
        self.classes = "list"
        self.border_title = "File explorer"

    async def on_mount(self) -> None:
        await self.populate(self.path)

    async def populate(self, directory: str | Path):
        """Populate the ListView with files and directories"""
        self.append(LabelItem("../", icon=ICON["directory"]))
        try:
            # Lazy load directory content
            children = get_directory_contents(directory, self)
            for chunk in range(0, len(children), 10):
                for child in children[chunk: chunk + 10]:
                    if child.is_dir():
                        icon = ICON["directory"]
                    else:
                        icon = (
                            ICON["audio"]
                            if child.suffix in ALLOWED_AUDIO_EXTENSIONS
                            else ICON["document"]
                        )
                    self.append(LabelItem(child.name, icon=icon))
        except Exception as e:
            self.notify(f"Error loading directory: {e}")

    @on(ListView.Selected)
    async def handle_selection(self, event: ListView.Selected):
        """Handle item selection from the filesystem."""
        selected_path = self.path.joinpath(event.item.label_text)

        if Path.is_dir(selected_path):
            if self.index == 0 or event.item.label_text == "../":
                self.path = Path(self.path).resolve().parent
            elif Path.is_dir(selected_path):
                self.path = selected_path

            await self.clear()
            await self.populate(self.path)
            self.focus()
            return

        if not is_valid_media(Path(selected_path)):
            return

        if not self.player.playing_song or self.player.playing_song != selected_path:
            self.player.play_song(selected_path)
            return

        self.player.toggle_play_state()

    async def action_add_to_playlist(self):
        """Add a media to the playlist."""
        media = self.path.joinpath(self.children[self.index].label_text)
        if not is_valid_media(media):
            return

        await self.parent.query_one("#playlist").add_media(media)


class Playlist(ListView):
    """Playlist filled by the user."""

    songs: dict[str, str] = reactive({})
    BINDINGS = [
        ("x", "remove_media", "Remove from the playlist"),
    ]

    def __init__(self, player: Widget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.player = player
        self.classes = "list"
        self.border_title = "Playlist"

    async def on_mount(self) -> None:
        # await self.populate(self.path)
        ...

    @on(ListView.Selected)
    async def handle_selection(self, event: ListView.Selected):
        """Handle media selection from the playlist."""
        key = event.item.label_text
        selected_media = self.songs[key]

        if (
            not self.player.playing_song
            or self.player.playing_song != selected_media
            or not self.player.playing_from_playlist
        ):
            self.player.play_from_playlist((key, selected_media))
            return

        self.player.toggle_play_state()

    async def populate(self):
        """Populate the Playlist with the current media list."""
        for child in self.songs:
            self.append(
                LabelItem(
                    child,
                    icon=ICON["audio"],
                )
            )

    async def add_media(self, media: str | Path) -> None:
        """Handle media addition to the playlist."""
        title, artist, _, _ = get_metadata(media)
        key = f"{title} {'~ ' + artist if artist != 'Unknown' else ''}"

        if key in self.songs:
            return

        self.songs[key] = media
        self.append(
            LabelItem(
                key,
                icon=ICON["audio"],
            )
        )

    async def action_remove_media(self) -> None:
        """Handle media removal from the playlist."""
        index = self.index
        media = self.children[index].label_text
        del self.songs[media]
        await self.children[index].remove()

        if not len(self.children):
            return

        self.index = index if index < len(self.children) else 0
