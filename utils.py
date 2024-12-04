from enum import Enum
from functools import lru_cache
from pathlib import Path

import pygame


class State(Enum):
    STOPPED: int = 0
    PLAYING: int = 1
    PAUSED: int = 2


class Loop(Enum):
    NONE: int = ""
    ONE: int = "1"
    ALL: int = "A"


ICON = {"directory": "📁", "file": "📄"}

ALLOWED_FILTYPES = [".wav", ".mp3", ".m4a"]


@lru_cache(maxsize=32)
def get_directory_contents(directory: Path, parent) -> list[str]:
    """Get the directory contents (files and directories)."""
    try:
        return sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        parent.notify("Permission denied.")
        return []


@lru_cache(maxsize=20)
def get_metadata(filepath: Path) -> list[str]:
    """Get the relevant info from the audio file."""
    media_info = pygame.mixer.music.get_metadata(filepath)
    return [
        media_info["title"] or filepath.stem,
        media_info["artist"] or "Unknown Artist",
        media_info["album"] or "Unknown Album",
    ]
