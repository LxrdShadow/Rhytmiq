from pathlib import Path

import pygame

pygame.mixer.init()


def play(file: Path) -> None:
    """Play a media file.

        Returns:
            True if the file was loaded successfuly.
            False otherwise.
    """
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        return True
    except Exception:
        return False


def pause() -> None:
    """Pause the media in the stream."""
    pygame.mixer.music.pause()


def unpause() -> None:
    """Unpause the media in the stream."""
    pygame.mixer.music.unpause()


def stop() -> None:
    """Stop the media in the stream."""
    pygame.mixer.music.stop()
