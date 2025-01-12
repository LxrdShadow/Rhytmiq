from functools import lru_cache
from pathlib import Path

from tinytag import TinyTag

from utils.constants import ALLOWED_AUDIO_EXTENSIONS


@lru_cache(maxsize=20)
def get_metadata(filepath: Path) -> list[str]:
    """Get the relevant info from the audio file."""
    media_info = TinyTag.get(filepath)
    return [
        media_info.title or filepath.stem,
        media_info.artist or "Unknown Artist",
        media_info.album or "Unknown Album",
        media_info.duration or 0,
    ]


def is_valid_media(filepath: Path) -> bool:
    return filepath.suffix in ALLOWED_AUDIO_EXTENSIONS
