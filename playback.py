import pygame

pygame.mixer.init()


def play(file: str) -> None:
    """Play a media file."""
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def pause() -> None:
    """Pause the media in the stream."""
    pygame.mixer.music.pause()


def unpause() -> None:
    """Unpause the media in the stream."""
    pygame.mixer.music.unpause()


def stop() -> None:
    """Stop the media in the stream."""
    pygame.mixer.music.stop()
