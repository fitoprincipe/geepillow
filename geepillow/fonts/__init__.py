import os
from PIL import ImageFont as fontmodule
from PIL.ImageFont import ImageFont, FreeTypeFont, TransposedFont
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import io
from pathlib import Path

try:
    from importlib.resources import open_binary
except ImportError:
    from pkg_resources import resources_stream as open_binary

from typing import Union

URL_FONT = 'http://db.onlinewebfonts.com/t/8050e6017c3b848b20a6324507cfba88.ttf'


def load_data(filename: Path):
    """Load binary data from filename"""
    if filename.is_absolute():
        with open(filename, 'b') as thefile:
            return thefile.read()
    else:
        with open_binary(__name__, filename) as thefile:
            return thefile.read()


def load_ttf(filename: Path, size: float) -> ImageFont:
    """Load a Font from a file.

    Args:
        filename: path of the font. If absolute path it will load it directly,
            if relative it will load one of the available in the package.
        size: size of the
    """
    bdata = load_data(filename)
    font_file = io.BytesIO(bdata)
    return fontmodule.truetype(font_file, size)


def join(name):
    """ join helper """
    return os.path.join(os.getcwd(), name)


def provided(size):
    """ Get font from URL """
    b = urllib2.urlopen(URL_FONT)
    font_file = io.BytesIO(b.read())
    return fontmodule.truetype(font_file, size)


opensans_bold = lambda size: load_ttf(Path('OpenSans-Bold.ttf'), size)
opensand_bold_italic = lambda size: load_ttf(Path('OpenSans-BoldItalic.ttf'), size)
opensans_italic = lambda size: load_ttf(Path('OpenSans-Italic.ttf'), size)
opensans_light = lambda size: load_ttf(Path('OpenSans-Light.ttf'), size)
opensans_regular = lambda size: load_ttf(Path('OpenSans-Regular.ttf'), size)


def create(font: Union[str, ImageFont, Path], size: float) -> ImageFont:
    if isinstance(font, str):
        if not font.endswith('.ttf'):
            font = f'{font}.ttf'
        return load_ttf(Path(font), size)
    if isinstance(font, (ImageFont, FreeTypeFont, TransposedFont)):
        return font
    if isinstance(font, Path):
        return load_ttf(font, size)
    raise ValueError(f"Font '{font}' format not recognized")
