import os
from enum import Enum
from pathlib import PosixPath
from typing import List

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Header,
    ListItem,
    ListView,
    ProgressBar,
    Static,
)
from tinytag import TinyTag

from playback import pause, play, pygame, stop, unpause

audio = TinyTag.get("song.mp3")
print("Title: " + audio.title)
print("Artist: " + audio.artist)


class State(Enum):
    STOPPED: int = 0
    PLAYING: int = 1
    PAUSED: int = 2


class FileExplorer(Static):
    """The album cover for the current media"""

    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = title

    async def on_mount(self) -> None:
        self.border_title = self.title

    def compose(self) -> ComposeResult:
        # self.list_view = ListView(
        #     ListItem(Static("Hello")),
        #     *[ListItem(Static(item)) for item in os.listdir()],
        #     id="file-explorer"
        # )
        self.list_view = DirectoryTree(os.getcwd(), id="file-explorer")
        yield self.list_view


class MediaPlayer(Vertical):
    """A media player widget."""

    state = State.STOPPED

    shuffle_button = Button("SH", id="shuffle", classes="control-buttons")
    prev_button = Button("PR", id="prev", classes="control-buttons")
    play_button = Button("PL", id="play", classes="control-buttons")
    # pause_button = Button("PA", id="pause", classes="control-buttons")
    next_button = Button("NX", id="next", classes="control-buttons")
    loop_button = Button("LO", id="loop", classes="control-buttons")

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
