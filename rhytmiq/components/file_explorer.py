from functools import lru_cache
from pathlib import Path

from textual import on
from textual.widget import Widget
from textual.widgets import ListView

from components.label_item import LabelItem
from utils.constants import ALLOWED_AUDIO_EXTENSIONS, ICON
from utils.helpers import is_valid_media


class FileExplorer(ListView):
    """A minimal file explorer for the player."""

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

    async def populate(self, directory: str | Path) -> None:
        """Populate the ListView with files and directories"""
        self.append(LabelItem("../", icon=ICON["directory"]))
        try:
            # Lazy load directory content
            children = self.get_directory_contents(directory)
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

    @lru_cache(maxsize=32)
    def get_directory_contents(self, directory) -> list[str]:
        """Get a directory's sorted contents (files and directories)."""
        try:
            return sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            self.notify("Permission denied.")
            return []

    @on(ListView.Selected)
    async def handle_selection(self, event: ListView.Selected) -> None:
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

        if (
            not self.player.playing_song
            or self.player.playing_song != selected_path
            or self.player.playing_from_playlist
        ):
            self.player.play_song(selected_path)
            return

        self.player.toggle_play_state()

    async def action_add_to_playlist(self) -> None:
        """Add a media to the playlist."""
        media = self.path.joinpath(self.children[self.index].label_text)
        if not is_valid_media(media):
            return

        await self.parent.query_one("#playlist").add_media(media)
