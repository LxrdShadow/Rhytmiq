from enum import Enum
from functools import lru_cache
from pathlib import Path

from tinytag import TinyTag


class State(Enum):
    STOPPED: int = 0
    PLAYING: int = 1
    PAUSED: int = 2


class Loop(Enum):
    NONE: str = ""
    ONE: str = "(1)"
    ALL: str = "(A)"


ICON = {
    "directory": "📁",
    "document": "📄",
    "audio": "📀",
    "video": "🎥",
    "image": "🖼️",
    "package": "📦"
}

ALLOWED_AUDIO_EXTENSIONS = [".mp3", ".wav", ".m4a"]
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv"]


@lru_cache(maxsize=32)
def get_directory_contents(directory: Path, parent) -> list[str]:
    """Get a directory's sorted contents (files and directories)."""
    try:
        return sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        parent.notify("Permission denied.")
        return []


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
