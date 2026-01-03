import time
import nava
import sys

from importlib.resources import files
from rich.live import Live
from rich.text import Text
from rich.style import Style
from rich.color import Color


HAPPY_NY = """
۰̮̑●̮̑۰★⋰⋱☆⋰⋱★⋰⋱☆⋰⋱★⋰⋱☆⋰⋱★۰̮̑●̮̑۰
──────█─█ █▀█ █▀█ █▀█ █─█─────
──────█▀█ █▀█ █▀▀ █▀▀ ▀█▀─────
──────▀─▀ ▀─▀ ▀── ▀── ─▀──────
█▄─█ █▀▀ █─█─█──█─█ █▀▀ █▀█ █▀█
█─██ █▀▀ █─█─█──▀█▀ █▀▀ █▀█ ██▀
▀──▀ ▀▀▀ ─▀▀▀────▀─ ▀▀▀ ▀─▀ ▀─▀
۰̮̑●̮̑۰★⋰⋱☆⋰⋱★⋰⋱☆⋰⋱★⋰⋱☆⋰⋱★۰̮̑●̮̑۰
"""


def play_sound() -> int | None:
    file = files("clelia_ny2026").joinpath("fireworks.mp3")
    if file.is_file():
        thread_id = nava.play(sound_path=str(file), async_mode=True)
    else:
        print("File not found")
        thread_id = None
    return thread_id


def main() -> None:
    with_sound = False
    if len(sys.argv) == 2 and sys.argv[1] == "sound":
        with_sound = True
    text_split = HAPPY_NY.splitlines(keepends=True)
    text = Text(
        text=text_split[0],
        style=Style(color=Color.from_rgb(245, 161, 39)),
        justify="full",
    )
    thread_id: int | None = None
    if with_sound:
        thread_id = play_sound()
    with Live(text, refresh_per_second=4):
        for t in text_split:
            time.sleep(0.5)
            text.append_text(text=Text(text=t))
    if thread_id is not None:
        nava.stop(thread_id)
