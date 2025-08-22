"""Fonts module."""

import sys
from functools import lru_cache

from PIL import ImageFont as fontmodule
from PIL.ImageFont import FreeTypeFont, ImageFont, TransposedFont

if sys.version_info[0] > 2:
    import urllib.request as urllib2
else:
    import urllib2

import io
from pathlib import Path

if sys.version_info > (3, 7):
    from importlib.resources import open_binary
else:
    from pkg_resources import resources_stream as open_binary

URL_FONT = "http://db.onlinewebfonts.com/t/8050e6017c3b848b20a6324507cfba88.ttf"


def load_data(filename: Path):
    """Load binary data from filename."""
    if filename.is_absolute():
        with open(filename, "b") as thefile:
            return thefile.read()
    else:
        with open_binary(__name__, filename.as_posix()) as thefile:
            return thefile.read()


@lru_cache(maxsize=128)
def load_ttf(filename: Path, size: float) -> FreeTypeFont:
    """Load a Font from a file.

    Args:
        filename: path of the font. If absolute path it will load it directly,
            if relative it will load one of the available in the package.
        size: size of the
    """
    bdata = load_data(filename)
    font_file = io.BytesIO(bdata)
    return fontmodule.truetype(font_file, size)


@lru_cache(maxsize=128)
def provided(size) -> FreeTypeFont:
    """Get font from URL."""
    b = urllib2.urlopen(URL_FONT)
    font_file = io.BytesIO(b.read())
    return fontmodule.truetype(font_file, size)


def opensans_bold(size: int) -> FreeTypeFont:
    """OpenSans-Bold."""
    return load_ttf(Path("OpenSans-Bold.ttf"), size)


def opensans_bold_italic(size: int) -> FreeTypeFont:
    """OpenSans-BoldItalic."""
    return load_ttf(Path("OpenSans-BoldItalic.ttf"), size)


def opensans_italic(size: int) -> FreeTypeFont:
    """OpenSans-Italic."""
    return load_ttf(Path("OpenSans-Italic.ttf"), size)


def opensans_light(size: int) -> FreeTypeFont:
    """OpenSans-Light."""
    return load_ttf(Path("OpenSans-Light.ttf"), size)


def opensans_regular(size: int) -> FreeTypeFont:
    """OpenSans-Regular."""
    return load_ttf(Path("OpenSans-Regular.ttf"), size)


def create(font: str | ImageFont | Path, size: float) -> ImageFont | FreeTypeFont | TransposedFont:
    """Create a font."""
    if isinstance(font, str):
        if not font.endswith(".ttf"):
            font = f"{font}.ttf"
        return load_ttf(Path(font), size)
    if isinstance(font, (ImageFont, FreeTypeFont, TransposedFont)):
        if hasattr(font, "path") and hasattr(font, "size") and font.path and font.size != size:
            return load_ttf(Path(font.path), size)
        return font
    if isinstance(font, Path):
        return load_ttf(font, size)
    raise ValueError(f"Font '{font}' format not recognized")
