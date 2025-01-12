from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, ProgressBar, Static


class MediaInfo(Horizontal):
    """Displaying the media info"""

    def __init__(self, audio_title: str, artist_name: str, album: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_title = audio_title
        self.artist_name = artist_name
        self.album = album

        self.progress_bar = ProgressBar(
            total=100, show_eta=False, show_percentage=False, id="volume-progress"
        )

    def compose(self) -> ComposeResult:
        yield Vertical(
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
        )
        yield Horizontal(
            Button("-", id="decrease-volume", classes="volume-buttons"),
            self.progress_bar,
            Button("+", id="increase-volume", classes="volume-buttons"),
            classes="volume-control",
        )
