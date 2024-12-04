from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static

from components import ControlButtons, FileExplorer, MediaInfo
from playback import pause, play, pygame, stop, unpause
from utils import State, get_metadata


class MediaPlayer(Container):
    """The main media player widget."""

    audio_title: str = reactive("No title available")
    artist_name: str = reactive("Unknown artist")
    album: str = reactive("No album info")
    state: State = reactive(State.STOPPED)
    duration: float = reactive(0)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.playing_song: Path = None

        # Children
        self.media_info = MediaInfo(
            self.audio_title,
            self.artist_name,
            self.album,
            classes="media-info",
        )

        self.control_buttons = ControlButtons(
            classes="control-buttons-group",
        )

    async def on_mount(self) -> None: ...

    def compose(self) -> ComposeResult:
        """Create child widgets for the player."""

        yield Container(
            Horizontal(
                FileExplorer(title="File explorer", player=self),
                FileExplorer(title="Playlist", player=self),
                classes="files",
            ),
            self.media_info,
            self.control_buttons,
            classes="media-player-container",
        )

    def play_song(self, media: str = "") -> None:
        """Manages playing new songs."""
        if not media:
            return

        play(media)
        self.playing_song = media
        self.audio_title, self.artist_name, self.album, self.duration = get_metadata(
            Path(media)
        )
        self.state = State.PLAYING

    @on(Button.Pressed, "#play")
    def toggle_play_state(self) -> None:
        """Toggle between play and pause state."""
        if self.state == State.PLAYING:
            pause()
            self.state = State.PAUSED
            return

        if self.state == State.PAUSED:
            unpause()
            self.state = State.PLAYING
            return

    # WATCHERS
    def watch_audio_title(self, old_value, new_value) -> None:
        try:
            self.query_one("#media-title", Static).update(new_value)
        except NoMatches:
            pass

    def watch_artist_name(self, old_value, new_value) -> None:
        try:
            self.query_one("#artist-name", Static).update(new_value)
        except NoMatches:
            pass

    def watch_album(self, old_value, new_value) -> None:
        try:
            self.query_one("#album", Static).update(new_value)
        except NoMatches:
            pass

    def watch_state(self, old_value, new_value) -> None:
        try:
            play_button = self.query_one("#play", Button)
            if self.state == State.PLAYING:
                play_button.label = "pause"
            else:
                play_button.label = "play"

        except NoMatches:
            pass


class Proxima(App):
    """
    A modern terminal-based media player.
    """

    CSS_PATH = "style.css"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("space", "toggle_play", "Toggle play"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.media_player = MediaPlayer()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield self.media_player

    def action_toggle_play(self):
        """Toggle between play and pause state from binding."""
        self.media_player.toggle_play_state()

    def action_quit(self):
        """Close the application"""
        stop()
        pygame.mixer.quit()
        self.exit()
