import argparse

from proxima import Proxima

# import os
# os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="Proxima", description="A modern terminal-based media player"
    )
    parser.add_argument("--folder", type=str, help="Path to the music folder")
    parser.add_argument("--play", type=str, help="Name of the media to play")
    parser.add_argument(
        "--volume",
        type=int,
        default=50,
        help="Initial volume for the player (0 to 100)",
    )

    return parser.parse_args()


def hello():
    print("hello")


def main():
    args = parse_arguments()
    print(args)
    proxima = Proxima()
    proxima.run()


if __name__ == "__main__":
    main()
