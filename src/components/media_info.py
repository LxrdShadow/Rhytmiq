from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class MediaInfo(Vertical):
    """Displaying the media info"""

    def __init__(self, audio_title: str, artist_name: str, album: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_title = audio_title
        self.artist_name = artist_name
        self.album = album

    def compose(self) -> ComposeResult:
        yield Static(
            self.audio_title,
            id="media-title",
            classes="media-info-texts",
        )
        yield Static(
            self.artist_name,
            id="artist-name",
            classes="media-info-texts",
        )
        yield Static(
            self.album,
            id="album",
            classes="media-info-texts",
        )
