import argparse
import os

# Disable the pygame's version support text
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from app import Rhytmiq
from config import APP_DESCRIPTION, APP_NAME


def parse_arguments(args=[]):
    parser = argparse.ArgumentParser(
        prog=APP_NAME, description=APP_DESCRIPTION,
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
    if args:
        ...
    rhytmiq = Rhytmiq()
    rhytmiq.run()


if __name__ == "__main__":
    main()
