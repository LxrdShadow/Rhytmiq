from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static

from playback import pause, play, pygame, stop, unpause
from utils import ALLOWED_FILTYPES, ICON, State, get_directory_contents, get_metadata


class LabelItem(ListItem):
    """Custom Label as a ListItem"""

    def __init__(self, label: str, icon: str = "") -> None:
        super().__init__()
        self.label = label
        self.icon = icon

    def compose(self) -> ComposeResult:
        yield Label(self.icon + self.label)


class MediaPlayer(Vertical):
    """A media player widget."""

    audio_title: str = reactive("No title available")
    artist_name: str = reactive("Unknown artist")
    album: str = reactive("No album info")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state: State = State.STOPPED
        self.playing_song: Path = None

    shuffle_button = Button("🔀", id="shuffle", classes="control-buttons")
    prev_button = Button("⏮️", id="prev", classes="control-buttons")
    play_button = Button("▶️", id="play", classes="control-buttons")
    # pause_button = Button("PA", id="pause", classes="control-buttons")
    next_button = Button("⏭️", id="next", classes="control-buttons")
    loop_button = Button("🔁", id="loop", classes="control-buttons")

    async def on_mount(self) -> None: ...

    @on(Button.Pressed, "#play")
    def handle_play_song(self, event: Button.Pressed) -> None:
        self.play_song()

    def play_song(self, media: str = "") -> None:
        if not media:
            return

        self.notify(str(self.playing_song))
        self.notify(str(media))

        if self.state == State.PLAYING and self.playing_song == media:
            pause()
            self.state = State.PAUSED
            return

        if self.state == State.PAUSED and self.playing_song == media:
            unpause()
            self.state = State.PLAYING
            return

        self._play_new_song(media)

    def _play_new_song(self, media: str) -> None:
        """Handles playing a new song and updating metadata."""
        play(media)
        self.playing_song = media
        self.audio_title, self.artist_name, self.album = get_metadata(media)
        self.state = State.PLAYING

    def compose(self) -> ComposeResult:
        """Create child widgets for the player."""

        yield Container(
            Horizontal(
                FileExplorer(title="File explorer", player=self, id="ac1"),
                FileExplorer(title="Playlist", player=self, id="ac2"),
                classes="files",
            ),
            Horizontal(
                Vertical(
                    Static(
                        self.audio_title,
                        id="media-title",
                        classes="media-info-texts",
                    ),
                    Static(
                        self.artist_name,
                        id="artist-name",
                        classes="media-info-texts",
                    ),
                    Static(
                        self.album,
                        id="album",
                        classes="media-info-texts",
                    ),
                    # ProgressBar(100, show_percentage=False, id="progress-bar"),
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

    def watch_audio_title(self, old_value, new_value):
        try:
            self.query_one("#media-title", Static).update(new_value)
        except NoMatches:
            pass

    def watch_artist_name(self, old_value, new_value):
        try:
            self.query_one("#artist-name", Static).update(new_value)
        except NoMatches:
            pass

    def watch_album(self, old_value, new_value):
        try:
            self.query_one("#album", Static).update(new_value)
        except NoMatches:
            pass


class FileExplorer(Container):
    """The album cover for the current media"""

    def __init__(self, title: str, player: MediaPlayer, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = title
        self.path = Path.cwd()
        self.player = player

    async def on_mount(self) -> None:
        self.border_title = self.title
        # await self.populate_list(self.path)

    def compose(self) -> ComposeResult:
        self.list_view = ListView(
            LabelItem("../", icon=ICON["directory"]),
            *[
                (
                    LabelItem(elem.name + "/", icon=ICON["directory"])
                    if elem.is_dir()
                    else LabelItem(elem.name, icon=ICON["file"])
                )
                for elem in get_directory_contents(self.path, self)
            ],
            id="file-explorer",
        )
        # self.list_view = DirectoryTree(os.getcwd(), id="file-explorer")
        yield self.list_view

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
        selected_path = self.path.joinpath(event.item.label)
        # self.notify(str(self.player.playing_song) or "")

        if (
            Path.is_file(selected_path)
            and Path(selected_path).suffix in ALLOWED_FILTYPES
        ):
            if (
                not self.player.playing_song
                or self.player.playing_song != selected_path
            ):
                self.player.play_song(selected_path)
            return

        if self.list_view.index == 0:
            self.path = Path(self.path).resolve().parent
        elif Path.is_dir(selected_path):
            self.path = selected_path

        # self.list_view.clear()
        # await self.populate_list(self.path)
        # self.list_view.focus()
        await self.recompose()
        self.list_view.focus()


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
