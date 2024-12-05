from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static

from components import ControlButtons, FileExplorer, MediaInfo, Playlist
from playback import pause, play, pygame, stop, unpause
from utils import Loop, State, get_metadata


class MediaPlayer(Container):
    """The main media player widget."""

    BINDINGS = [
        ("space", "toggle_play", "Toggle play"),
    ]

    audio_title: str = reactive("No title available")
    artist_name: str = reactive("Unknown artist")
    album: str = reactive("No album info")
    duration: float = reactive(0)
    state: State = reactive(State.STOPPED)
    shuffle: bool = reactive(False)
    loop: Loop = reactive(Loop.NONE)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.playing_song: Path = None
        self.classes = "media-player-container"

        # Children
        self.file_explorer = FileExplorer(player=self, id="file-explorer")
        self.playlist = Playlist(player=self, id="playlist")

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

        yield Horizontal(
                self.file_explorer,
                self.playlist,
                classes="files",
            )
        yield self.media_info
        yield self.control_buttons

    def play_song(self, media: str | Path = "") -> None:
        """Manages playing new songs."""
        if not media:
            return

        if play(Path(media)):
            self.playing_song = media
            self.audio_title, self.artist_name, self.album, self.duration = get_metadata(
                Path(media)
            )
            self.state = State.PLAYING
        else:
            self.notify("Unable to play the media file.")

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

    # WATCHERS for dynamic text reloading
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

    def watch_shuffle(self, old_value, new_value) -> None:
        try:
            shuffle_button = self.query_one("#shuffle", Button)
            if self.shuffle:
                shuffle_button.label = "shuffle 🮱"
            else:
                shuffle_button.label = "shuffle"

        except NoMatches:
            pass

    def watch_loop(self, old_value, new_value) -> None:
        try:
            self.query_one("#loop", Button).label = f"loop {new_value.value}"
        except NoMatches:
            pass

    # BINDING Actions
    def action_toggle_play(self):
        """Toggle between play and pause state from binding."""
        self.toggle_play_state()


class Proxima(App):
    """
    A modern terminal-based media player.
    """

    CSS_PATH = "style.css"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.media_player = MediaPlayer()
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Footer()
        yield self.media_player

    def action_quit(self):
        """Close the application"""
        print("Exiting...")
        stop()
        pygame.mixer.quit()
        self.exit()
