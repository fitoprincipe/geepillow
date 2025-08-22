"""Blocks module.

Blocks are the basic units to use in strips and grids, and do not overlay with each other.

There are 2 types:

- ImageBlock: contains an image inside.
- TextBlock: contains text inside.

If the user needs to add text overlaying the image, can do it using the PIL library.
"""

from pathlib import Path
from typing import Literal, Union

from PIL import Image as ImPIL
from PIL import ImageDraw
from PIL.ImageFont import FreeTypeFont, ImageFont, TransposedFont

from geepillow import colors, fonts
from geepillow.colors import Color

DEFAULT_FONT = fonts.opensans_regular(12)
DEFAULT_MODE = "RGBA"

FontType = Union[ImageFont, FreeTypeFont, TransposedFont]

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

    def __init__(
        self,
        size: tuple = DEFAULT_SIZE,
        background_color: str | Color = "white",
        background_opacity: float = 1,
        mode: str = DEFAULT_MODE,
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
            mode: mode of the background image.
        """
        self._size = size or self.DEFAULT_SIZE
        self._width, self._height = self._size
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        self.mode = mode

    @property
    def image(self):
        """For basic blocks the image is the background image."""
        return self.background_image

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
        size[1] = height
        self._size = tuple(size)

    @property
    def background_image(self):
        """The background image."""
        im = ImPIL.new(self.mode, self.size, self.background_hex)
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
        background_opacity: float = 1,
        mode: str = DEFAULT_MODE,
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
            mode: mode of the background image.
        """
        size = size or image.size
        # convert image to the block mode
        self._image = image.convert(mode)  # store the original image
        super(ImageBlock, self).__init__(
            size=size,
            background_color=background_color,
            background_opacity=background_opacity,
            mode=mode,
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
        im = self.background_image
        im.paste(self.element, self.xy)
        return im

    @classmethod
    def from_file(cls, filename: str | Path, **kwargs):
        """Create an ImageBlock from a file."""
        filename = Path(filename)
        return cls(ImPIL.open(filename), **kwargs)


class TextBlock(ImageBlock):
    """TextBlock."""

    def __init__(
        self,
        text: str,
        position: tuple | PositionType = "center-center",
        font: FontType = DEFAULT_FONT,
        text_color: str | Color = "black",
        text_opacity: float | int = 1,
        background_color: str | Color = "white",
        background_opacity: float | int = 1,
        fit_block: bool = False,
        keep_proportion: bool = True,
        size: tuple | None = None,
        mode: str = DEFAULT_MODE,
    ):
        """TextBlock.

        Args:
            text: text to display.
            position: position of the text inside the block.
            font: font to use. The size the font is included in this parameter.
            text_color: color of the text.
            text_opacity: opacity of the text.
            background_color: color of the background.
            background_opacity: opacity of the background.
            fit_block: if True the element'
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image). Defaults to the image size.
            mode: mode of the background image.
        """
        self._text = text
        self._text_color = colors.create(text_color)
        self.text_opacity = text_opacity
        self._font = font
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        self.mode = mode
        super(TextBlock, self).__init__(
            image=self.create_text_image(),
            position=position,
            fit_block=fit_block,
            keep_proportion=keep_proportion,
            background_opacity=background_opacity,
            background_color=background_color,
            size=size,
            mode=mode,
        )

    @property
    def text(self) -> str:
        """Text to display."""
        return self._text

    @property
    def font(self):
        """Font to use."""
        return self._font

    @font.setter
    def font(self, font: ImageFont | FreeTypeFont | TransposedFont):
        """Set or modify the font to use."""
        self._font = font
        self._image = self.create_text_image()

    @property
    def text_color(self) -> Color:
        """Text color."""
        return self._text_color

    @text_color.setter
    def text_color(self, color: str | Color):
        """Set or modify the text color."""
        self._text_color = colors.create(color)

    @property
    def text_height(self) -> int:
        """Calculate height for a multiline text."""
        alist = self.text.split("\n")
        alt = 0
        for line in alist:
            alt += self.font.getbbox(line)[3] + self.font.getbbox(line)[1]
        return int(alt)

    @property
    def text_width(self) -> int:
        """Calculate width for a multiline text."""
        alist = self.text.split("\n")
        widths = []
        for line in alist:
            w = self.font.getbbox(line)[2]
            widths.append(w)
        return int(max(widths))

    def create_text_image(self) -> ImPIL.Image:
        """Create a text image."""
        image = ImPIL.new(self.mode, (self.text_width, self.text_height), self.background_hex)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), self.text, font=self.font, fill=self.text_color.hex(self.text_opacity))
        return image
