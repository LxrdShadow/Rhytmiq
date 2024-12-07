from enum import Enum


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

ALLOWED_AUDIO_EXTENSIONS = [".mp3", ".wav", ".m4a", ".flac"]
VIDEO_EXTENSIONS = [".mp4", ".avi", ".mkv"]
