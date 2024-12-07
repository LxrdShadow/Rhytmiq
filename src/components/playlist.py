
from pathlib import Path
from textual import on
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ListView

from components.label_item import LabelItem
from utils.constants import ICON
from utils.helpers import get_metadata


class Playlist(ListView):
    """A minimal playlist for the player."""

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
        key = f"{title} {'~ ' + artist}"

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
