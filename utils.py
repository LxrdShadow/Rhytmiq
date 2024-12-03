from enum import Enum
from functools import lru_cache
from pathlib import Path

from tinytag import TinyTag


class State(Enum):
    STOPPED: int = 0
    PLAYING: int = 1
    PAUSED: int = 2


ICON = {"directory": "📁", "file": "📄"}

ALLOWED_FILTYPES = [".wav", ".mp3", ".m4a"]


@lru_cache(maxsize=32)
def get_directory_contents(directory: Path, parent) -> list[str]:
    try:
        return sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        parent.notify("Permission denied.")
        return []


@lru_cache(maxsize=20)
def get_metadata(filepath) -> list[str]:
    media_info = TinyTag.get(filepath)
    return [
        media_info.title or "Unknown",
        media_info.artist or "Unknown Artist",
        media_info.album or "Unknown Album",
    ]
