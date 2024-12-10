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


def increase_volume(amount: float) -> None:
    """Increase the volume"""
    current_volume = pygame.mixer.music.get_volume()
    pygame.mixer.music.set_volume(
        current_volume + amount if amount + current_volume < 1 else 1
    )


def decrease_volume(amount: float) -> None:
    """Decrease the volume"""
    current_volume = pygame.mixer.music.get_volume()
    pygame.mixer.music.set_volume(
        current_volume - amount if amount < current_volume else 0
    )
