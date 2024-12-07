from pathlib import Path
from threading import Thread
from time import sleep

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
        self.current_playlist_title: str = None
        self.classes: str = "media-player-container"
        self.playing_from_playlist: bool = False
        self.monitor_thread: Thread = None
        self.running: bool = True
        self.state_switch: bool = False

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

    def compose(self) -> ComposeResult:
        """Create child widgets for the player."""

        yield Horizontal(
            self.file_explorer,
            self.playlist,
            classes="files",
        )
        yield self.media_info
        yield self.control_buttons

    def play_song(self, media: str | Path = "", from_playlist: bool = False) -> None:
        """Manages playing new songs."""
        if not media:
            return

        self.state_switch = True
        self.playing_from_playlist = from_playlist

        if play(media):
            self.playing_song = media
            self.audio_title, self.artist_name, self.album, self.duration = (
                get_metadata(media)
            )
            self.state = State.PLAYING

            if self.monitor_thread is None or not self.monitor_thread.is_alive():
                self.monitor_thread = Thread(target=self.monitor_song_end, daemon=True)
                self.monitor_thread.start()
        else:
            self.next_song()
            self.notify("Unable to play the media file.")

        self.state_switch = False

    def play_from_playlist(self, media: tuple[str]) -> None:
        """Manages playing songs from the playlist."""
        self.current_playlist_title, song = media

        self.play_song(song, from_playlist=True)

    def monitor_song_end(self) -> None:
        """Monitor when a song ends."""
        while self.running:
            if self.state_switch:
                sleep(0.5)
                continue

            if self.state == State.PLAYING and not pygame.mixer.music.get_busy():
                self.handle_song_end()
                sleep(0.5)

    def handle_song_end(self) -> None:
        """Called when a song finishes playing."""

        if self.state == State.PAUSED:
            return

        if not self.playing_from_playlist:
            if self.loop != Loop.NONE:
                self.play_song(self.playing_song)
            else:
                self.state = State.STOPPED
            return

        if not self.playlist.songs:
            self.state = State.STOPPED
            return

        self.next_song()

    @on(Button.Pressed, "#play")
    def toggle_play_state(self) -> None:
        """Toggle between play and pause state."""
        if self.state == State.PLAYING:
            pause()
            self.state = State.PAUSED
        elif self.state == State.PAUSED:
            unpause()
            self.state = State.PLAYING
        elif self.state == State.STOPPED and self.playing_song is not None:
            self.play_song(self.playing_song, from_playlist=self.playing_from_playlist)

    @on(Button.Pressed, "#loop")
    def change_loop_state(self) -> None:
        """Toggle between the loop states (NONE, ONE and ALL)."""
        if self.loop == Loop.NONE:
            self.loop = Loop.ONE
        elif self.loop == Loop.ONE:
            self.loop = Loop.ALL
        else:
            self.loop = Loop.NONE

    @on(Button.Pressed, "#next")
    def next_song(self) -> None:
        """Play the next media in the playlist."""
        if not self.playing_from_playlist and self.loop == Loop.NONE:
            stop()
            self.state = State.STOPPED
            return

        next_song_path = self.playing_song

        if self.playing_from_playlist and self.loop != Loop.ONE:
            titles = list(self.playlist.songs.keys())
            current_index = titles.index(self.current_playlist_title)

            if current_index + 1 < len(titles):
                new_index = current_index + 1
            elif self.loop == Loop.ALL:
                new_index = 0
            else:
                stop()
                self.state = State.STOPPED
                return

            next_song_title = titles[new_index]
            next_song_path = self.playlist.songs[next_song_title]
            self.current_playlist_title = next_song_title

        self.play_song(next_song_path, from_playlist=self.playing_from_playlist)

    @on(Button.Pressed, "#prev")
    def previous_song(self) -> None:
        """Play the previous media in the playlist."""
        if not self.playing_from_playlist and self.loop == Loop.NONE:
            stop()
            self.state = State.STOPPED
            return

        previous_song_path = self.playing_song

        if self.playing_from_playlist and self.loop != Loop.ONE:
            titles = list(self.playlist.songs.keys())
            current_index = titles.index(self.current_playlist_title)

            if current_index > 0:
                new_index = current_index - 1
            elif self.loop == Loop.ALL:
                new_index = len(titles) - 1
            else:
                stop()
                self.state = State.STOPPED
                return

            previous_song_title = titles[new_index]
            previous_song_path = self.playlist.songs[previous_song_title]
            self.current_playlist_title = previous_song_title

        self.play_song(previous_song_path, from_playlist=self.playing_from_playlist)

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
    A modern terminal-based music player.
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
        yield Header()
        yield Footer()
        yield self.media_player

    def action_quit(self):
        """Close the application"""
        self.media_player.running = False
        stop()
        pygame.mixer.quit()
        self.exit()
