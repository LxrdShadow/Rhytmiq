from main import parse_arguments


def test_parse_arguments_with_defaults():
    args = parse_arguments([])
    assert args.folder is None
    assert args.play is None
    assert args.volume == 50


def test_parse_arguments_with_values():
    args = parse_arguments(
        ["--folder", "/music", "--play", "song.mp3", "--volume", "80"]
    )
    assert args.folder == "/music"
    assert args.play == "song.mp3"
    assert args.volume == 80
