"""Blocks module."""

from typing import Literal

from PIL import Image as ImPIL
from PIL.ImageFont import FreeTypeFont, ImageFont, TransposedFont

from geepillow import colors, fonts
from geepillow.colors import Color

DEFAULT_FONT = fonts.opensans_regular(12)

FontType = ImageFont | FreeTypeFont | TransposedFont

PositionType = Literal[
    "top-left",
    "top-center",
    "top-right",
    "center-left",
    "center-center",
    "center-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]


class Block:
    """Basic Block."""

    DEFAULT_SIZE = (500, 500)
    DEFAULT_MODE = "RGBA"

    def __init__(
        self,
        size: tuple = DEFAULT_SIZE,
        background_color: str | Color = "white",
        background_opacity: float = 0,
    ):
        """Basic Block.

        The background will always be an image that will cover the whole block.
        Then the inner element will be painted on top of the background image.

        This object is mutable. All properties, except "element" can be
        modified.

        Args:
            size: size of the block in pixels.
            background_color: color of the background.
            background_opacity: opacity of the background.
        """
        self._size = size or self.DEFAULT_SIZE
        self._width, self._height = self._size
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity

    @property
    def image(self):
        """For basic blocks the image is the background image."""
        return self.background_image()

    @property
    def background_hex(self):
        """Background hex color."""
        return self.background_color.hex(self.background_opacity)

    @property
    def background_color(self):
        """Background color."""
        return self._background_color

    @background_color.setter
    def background_color(self, color: str | Color):
        """Set or modify the background color."""
        self._background_color = colors.create(color)

    @property
    def size(self):
        """Size of the block."""
        return self._size

    @size.setter
    def size(self, size: tuple):
        """Set or modify the size of the block."""
        self._size = size
        self._width = size[0]
        self._height = size[1]

    def set_size(self, size: tuple):
        """Set or modify the size of the block."""
        self.size = size

    @property
    def width(self):
        """Width of the block."""
        return self._width

    @width.setter
    def width(self, width: float):
        """Set or modify the width of the block."""
        self._width = width
        size = list(self.size)
        size[0] = width
        self._size = tuple(size)

    @property
    def height(self):
        """Height of the block."""
        return self._height

    @height.setter
    def height(self, height: float):
        """Set or modify the height of the block."""
        self._height = height
        size = list(self.size)
        size[0] = height
        self._size = tuple(size)

    def background_image(self, mode: str = "RGBA"):
        """The background image."""
        im = ImPIL.new(mode, self.size, self.background_hex)
        return im
