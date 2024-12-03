from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    ProgressBar,
    Static,
)
from tinytag import TinyTag

from playback import pause, play, pygame, stop, unpause
from utils import ICON, State, get_directory_contents

audio = TinyTag.get("song.mp3")
print("Title: " + audio.title)
print("Artist: " + audio.artist)


class LabelItem(ListItem):
    """Custom Label as a ListItem"""

    def __init__(self, label: str, icon: str = "") -> None:
        super().__init__()
        self.label = label
        self.icon = icon

    def compose(self) -> ComposeResult:
        yield Label(self.icon + self.label)


class FileExplorer(Container):
    """The album cover for the current media"""

    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = title
        self.path = Path.cwd()

    async def on_mount(self) -> None:
        self.border_title = self.title
        await self.populate_list(self.path)

    def compose(self) -> ComposeResult:
        self.list_view = ListView()
        # self.list_view = DirectoryTree(os.getcwd(), id="file-explorer")
        yield self.list_view
        self.populate_list(self.path)

    async def populate_list(self, directory: Path):
        """Populate the ListView with files and directories"""
        self.list_view.append(LabelItem("../", icon=ICON["directory"]))
        try:
            # Lazy load directory content
            children = get_directory_contents(directory, self)
            for chunk in range(0, len(children), 10):
                for child in children[chunk : chunk + 10]:
                    icon = ICON["directory"] if child.is_dir() else ICON["file"]
                    self.list_view.append(LabelItem(child.name, icon=icon))
        except Exception as e:
            self.notify(f"Error loading directory: {e}")

    @on(ListView.Selected)
    async def selected(self, event: ListView.Selected):
        """Handle item selection."""
        selected_path = event.item.label

        if Path.is_file(self.path.joinpath(selected_path)):
            self.notify("Playing...")
            return

        if self.list_view.index == 0:
            self.path = Path(self.path).resolve().parent
        elif Path.is_dir(self.path.joinpath(selected_path)):
            self.path = self.path.joinpath(selected_path)

        # self.list_view.clear()
        # await self.populate_list(self.path)
        # self.list_view.focus()
        await self.recompose()
        self.list_view.focus()


class MediaPlayer(Vertical):
    """A media player widget."""

    state = State.STOPPED

    shuffle_button = Button("🔀", id="shuffle", classes="control-buttons")
    prev_button = Button("⏮️", id="prev", classes="control-buttons")
    play_button = Button("▶️", id="play", classes="control-buttons")
    # pause_button = Button("PA", id="pause", classes="control-buttons")
    next_button = Button("⏭️", id="next", classes="control-buttons")
    loop_button = Button("🔁", id="loop", classes="control-buttons")

    async def on_mount(self) -> None: ...

    @on(Button.Pressed, "#play")
    def action_play(self, event: Button.Pressed) -> None:
        if self.state == State.STOPPED:
            play("song.mp3")
            self.state = State.PLAYING
        elif self.state == State.PAUSED:
            unpause()
            self.state = State.PLAYING
        else:
            pause()
            self.state = State.PAUSED

    def compose(self) -> ComposeResult:
        """Create child widgets for the player."""

        yield Container(
            Horizontal(
                FileExplorer(title="File explorer", id="ac1"),
                FileExplorer(title="Playlist", id="ac2"),
                classes="files",
            ),
            Horizontal(
                Vertical(
                    Static(
                        audio.title or "unknown",
                        id="media-title",
                        classes="media-info-texts",
                    ),
                    Static(
                        audio.artist or "unknown",
                        id="artist-name",
                        classes="media-info-texts",
                    ),
                    Static(
                        audio.album or "unknown",
                        id="album-name",
                        classes="media-info-texts",
                    ),
                    ProgressBar(100, show_percentage=False, id="progress-bar"),
                    classes="media-info",
                ),
                self.shuffle_button,
                self.prev_button,
                self.play_button,
                self.next_button,
                self.loop_button,
                classes="control-buttons-group",
            ),
        )


class Proxima(App):
    """
    A modern terminal-based media player.
    """

    CSS_PATH = "style.css"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield MediaPlayer()

    def action_quit(self) -> None:
        stop()
        pygame.mixer.quit()
        self.exit()
