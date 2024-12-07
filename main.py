import argparse
import os

# Disable the pygame's version support text
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from proxima import Proxima


def parse_arguments(args=[]):
    parser = argparse.ArgumentParser(
        prog="Proxima", description="A modern terminal-based music player."
    )
    parser.add_argument("--folder", type=str, help="Path to the choosen folder")
    parser.add_argument("--play", type=str, help="Name of the media to play")
    parser.add_argument(
        "--volume",
        type=int,
        default=50,
        help="Initial volume for the player (0 to 100)",
    )

    return parser.parse_args(args)


def main():
    args = parse_arguments()
    proxima = Proxima()
    proxima.run()


if __name__ == "__main__":
    main()
