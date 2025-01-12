import pygame
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from config import STYLE_FILE
from media_player import MediaPlayer
from utils.playback import stop


class Rhytmiq(App):
    """
    A modern terminal-based music player.
    """

    CSS_PATH = STYLE_FILE

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.media_player = MediaPlayer()
        self.dark = True
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

    def action_toggle_dark(self):
        """Close the application"""
        if self.dark:
            self.theme = "catppuccin-latte"
        else:
            self.theme = "tokyo-night"

        self.dark = not self.dark
