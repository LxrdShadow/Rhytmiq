import pygame

pygame.mixer.init()


def play(file: str):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def pause():
    pygame.mixer.music.pause()


def unpause():
    pygame.mixer.music.unpause()


def stop():
    pygame.mixer.music.stop()
