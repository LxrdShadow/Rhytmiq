from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static

from components import ControlButtons, FileExplorer, MediaInfo
from playback import pause, play, unpause
from utils import State, get_metadata


class MediaPlayer(Container):
    """The main media player widget."""

    audio_title: str = reactive("No title available")
    artist_name: str = reactive("Unknown artist")
    album: str = reactive("No album info")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.state: State = State.STOPPED
        self.playing_song: Path = None

    async def on_mount(self) -> None: ...

    @on(Button.Pressed, "#play")
    def handle_play_song(self, event: Button.Pressed) -> None:
        """Handle pressing the play button"""
        self.play_song()

    def play_song(self, media: str = "") -> None:
        """Manages clicking the play button"""
        if not media:
            return

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
        self.audio_title, self.artist_name, self.album = get_metadata(Path(media))
        self.state = State.PLAYING

    def compose(self) -> ComposeResult:
        """Create child widgets for the player."""

        yield Container(
            Horizontal(
                FileExplorer(title="File explorer", player=self, id="ac1"),
                FileExplorer(title="Playlist", player=self, id="ac2"),
                classes="files",
            ),
            MediaInfo(
                self.audio_title,
                self.artist_name,
                self.album,
                classes="media-info",
            ),
            ControlButtons(
                classes="control-buttons-group",
            ),
            classes="media-player-container",
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
