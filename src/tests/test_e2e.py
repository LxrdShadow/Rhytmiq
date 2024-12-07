import subprocess


def app_launch():
    result = subprocess.run(
        ["python", "main.py", "--folder", "~/", "--volume", "80"],
        text=True,
        capture_output=True,
    )

    assert "Running Proxima..." in result.stdout
    assert "Exiting..." in result.stdout
