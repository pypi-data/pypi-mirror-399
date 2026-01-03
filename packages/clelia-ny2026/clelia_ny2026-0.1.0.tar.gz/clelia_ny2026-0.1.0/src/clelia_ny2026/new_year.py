import time

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


def main() -> None:
    text_split = HAPPY_NY.splitlines(keepends=True)
    text = Text(
        text=text_split[0],
        style=Style(color=Color.from_rgb(245, 161, 39)),
        justify="full",
    )
    with Live(text, refresh_per_second=4):
        for t in text_split:
            time.sleep(0.5)
            text.append_text(text=Text(text=t))
