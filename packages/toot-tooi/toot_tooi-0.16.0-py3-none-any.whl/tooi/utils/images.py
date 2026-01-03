from functools import lru_cache
from pathlib import Path
from typing import Generator, Iterable

from PIL import Image
from rich.color import Color
from rich.style import Style
from rich.text import Text

from tooi import cache
from tooi.utils import batched
from tooi.utils.blurhash import blurhash_decode

ColorTuple = tuple[int, int, int]
Pixels = Iterable[list[ColorTuple]]


# TODO: cache this, can't lru_cache because it's async
async def render_remote(url: str, width: int, height: int) -> Text:
    path = await cache.download_image_cached(url)
    return await render_local(path, width, height)


async def render_local(path: str | Path, width: int, height: int) -> Text:
    image = _open_and_resize(path, width, height)
    return _encode(_image_pixels(image))


@lru_cache
def render_blurhash(blurhash: str, width: int, height: int, aspect_ratio: float | None = None) -> Text:
    return _encode(_blurhash_pixels(blurhash, width, height, aspect_ratio))


def render_plain_placeholder(width: int, height: int, aspect_ratio: float | None):
    width, height = _adjust_aspect_ratio(width, height, aspect_ratio)
    height = int(height / 2)  # height is in pixels, 1 char = 2 pixels
    style = Style(bgcolor=Color.from_rgb(50, 50, 50))
    return Text("\n".join(" " * width for _ in range(height)), style)


def render_placeholder(width: int, height: int, blurhash: str | None, aspect_ratio: float | None = None) -> Text:
    if blurhash:
        try:
            return render_blurhash(blurhash, width, height, aspect_ratio)
        except ValueError:
            pass
    return render_plain_placeholder(width, height, aspect_ratio)


def _open_and_resize(path: str | Path, width: int, height: int) -> Image.Image:
    image = Image.open(path)
    image.thumbnail((width, height))
    return image.convert("RGB")


def _image_pixels(image: Image.Image) -> Generator[list[ColorTuple], None, None]:
    pixels: list[tuple[int, int, int]] = list(image.getdata())  # type: ignore
    yield from batched(pixels, image.width)


def _blurhash_pixels(bhash: str, width: int, height: int, aspect_ratio: float | None = None) \
        -> Generator[list[ColorTuple], None, None]:
    width, height = _adjust_aspect_ratio(width, height, aspect_ratio)
    pixels = blurhash_decode(bhash, width, height)
    yield from batched(pixels, width)


def _adjust_aspect_ratio(width: int, height: int, target_aspect_ratio: float | None) -> tuple[int, int]:
    if not target_aspect_ratio:
        return width, height

    viewport_aspect_ratio = width / height
    if viewport_aspect_ratio >= target_aspect_ratio:
        # Viewport wider than target
        width = int(height * target_aspect_ratio)
    else:
        # Viewport taller than target
        height = int(width / target_aspect_ratio)

    return width, height


def _encode(pixels: Pixels) -> Text:
    half_block = "\N{lower half block}"
    text = Text()

    for row in batched(pixels, 2):
        # Handle odd numbered image height by repeating the last row
        if len(row) == 1:
            pairs = zip(row[0], row[0])
        else:
            pairs = zip(row[0], row[1])

        for top_color, bottom_color in pairs:
            style = Style(
                color=Color.from_rgb(*bottom_color),
                bgcolor=Color.from_rgb(*top_color),
            )

            text.append(half_block, style)
        text.append("\n")

    text.rstrip()
    return text
