import os
from enum import Enum
import pygame

pygame.init()
ALLOWED_FILTYPES = [".wav", ".mp3", ".m4a"]
FOLDER_PATH = os.getcwd()


class LoopType(Enum):
    NONE: int = 0
    ONE: int = 1
    ALL: int = 2


def load_single_song(folderpath: str):
    filename = input("Enter the name of the file: ")
    file = os.path.join(folderpath, filename)

    if not os.path.exists(file):
        print("File not found.")
        return

    if not os.path.isfile(file) or (os.path.splitext(file)[1] not in ALLOWED_FILTYPES):
        print("Can't read the file you specified.")
        return

    player([file])


def load_songs_in_folder(folderpath: str):
    print("play folder songs")


def player(files: list[str]):
    running = True
    current_index = 0
    LOOP_EVENT = pygame.USEREVENT
    loop = LoopType.ONE

    play_song(files[current_index])
    pygame.mixer.music.set_volume(.4)
    pygame.mixer.music.set_endevent(LOOP_EVENT)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type != LOOP_EVENT:
                ...
            elif loop == LoopType.NONE:
                running = False
            elif loop == LoopType.ONE:
                play_song(files[current_index])
            elif loop == LoopType.ALL:
                current_index = current_index + 1 if current_index < len(files) - 1 else 0
                play_song(files[current_index])

    stop_song()


def play_song(file: str):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()


def pause_song():
    pygame.mixer.music.pause()


def unpause_song():
    pygame.mixer.music.unpause()


def stop_song():
    pygame.mixer.music.stop()


def main():
    load_single_song(FOLDER_PATH)


if __name__ == "__main__":
    main()
