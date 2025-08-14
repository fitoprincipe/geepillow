"""Blocks module.

Blocks are the basic units to use in strips and grids, and do not overlay with each other.

There are 2 types:

- ImageBlock: contains an image inside.
- TextBlock: contains text inside.

If the user needs to add text overlaying the image, can do it using the PIL library.
"""

from pathlib import Path
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
        background_opacity: float = 1,
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


class ImageBlock(Block):
    def __init__(
        self,
        image: ImPIL.Image,
        position: tuple | PositionType = "center-center",
        fit_block: bool = True,
        keep_proportion: bool = True,
        size: tuple | None = None,
        background_color: str | Color = "white",
        background_opacity: float = 0,
    ):
        """Image Block for PIL images.

        Args:
            image: the image.
            position: position of the image inside the block.
            fit_block: if True the element's boundaries will never exceed the block.
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image). Defaults to the image size.
            background_color: color of the background.
            background_opacity: opacity of the background.
        """
        size = size or image.size
        self._image = image  # store the original image
        super(ImageBlock, self).__init__(
            size=size, background_color=background_color, background_opacity=background_opacity
        )
        self.position = position
        self.fit_block = fit_block
        self.keep_proportion = keep_proportion

    @property
    def xy(self):
        """Coordinates (X,Y) of the top-left corner of the inner image."""
        if isinstance(self.position, str):
            x_space = self.width - self.element.width
            y_space = self.height - self.element.height
            options = {
                "top-left": (0, 0),
                "top-center": (x_space / 2, 0),
                "top-right": (x_space, 0),
                "center-left": (0, y_space / 2),
                "center-center": (x_space / 2, y_space / 2),
                "center-right": (x_space, y_space / 2),
                "bottom-left": (0, y_space),
                "bottom-center": (x_space / 2, y_space),
                "bottom-right": (x_space, y_space),
            }
            try:
                pos = options[self.position]
            except KeyError:
                raise KeyError(f"Position '{self.position}' not in {list(options.keys())}")
            return int(pos[0]), int(pos[1])
        else:
            return self.position

    @property
    def element(self) -> ImPIL.Image:
        """Element.

        The original image will be modified according to size of the block and properties fit_block and keep_proportion.
        """
        # use the original image to compute the resizing parameters
        image_width, image_height = self._image.size
        block_width, block_height = self.size
        # is the image wider or higher than the block?
        is_wider, is_higher = image_width > block_width, image_height > block_height
        element = self._image
        if self.fit_block:
            # resize to fit the block
            if self.keep_proportion:
                proportion = self._image.size[0] / self._image.size[1]
                if is_wider and is_higher:
                    # fit according to the block proportions
                    if proportion >= 0:  # its width is more than its height
                        # adapt image to the block height
                        new_height = block_height
                        new_width = int(new_height * proportion)
                    else:
                        # adapt image to the block width
                        new_width = block_width
                        new_height = int(new_width / proportion)
                elif is_wider:  # is wider than the block but not higher
                    new_width = block_width
                    new_height = int(new_width / proportion)
                elif is_higher:  # is higher than the block but not wider
                    new_height = block_height
                    new_width = int(new_height * proportion)
                else:  # is not wider or higher than the block
                    new_width = image_width
                    new_height = image_height
                new_size = (new_width, new_height)
            else:
                new_size = (block_width, block_height)
            if new_size != self._image.size:
                # resize only is size changed
                element = element.resize(new_size)
        return element

    @property
    def image(self) -> ImPIL:
        """Image of the block."""
        im = self.background_image()
        im.paste(self.element, self.xy)
        return im

    @classmethod
    def from_file(cls, filename: str | Path, **kwargs):
        """Create an ImageBlock from a file."""
        filename = Path(filename)
        return cls(ImPIL.open(filename), **kwargs)
