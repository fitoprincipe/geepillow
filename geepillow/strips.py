"""A strip is a concatenation of blacks."""

from typing import Literal

from PIL import Image as ImPIL

from geepillow import colors
from geepillow.blocks import DEFAULT_MODE, Block, ImageBlock, PositionType


class Strip(ImageBlock):
    """Strip.

    A concatenation of blocks that behave like a block.
    """

    def __init__(
        self,
        blocks: list[Block],
        space: float = 10,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        proxy_block: Block | None = None,
        position: tuple | PositionType = "center-center",
        fit_block: bool = True,
        keep_proportion: bool = True,
        size: tuple | None = None,
        background_color: str | colors.Color = "white",
        background_opacity: float = 1,
        mode: str = DEFAULT_MODE,
    ):
        """Strip.

        A concatenation of blocks that behave like a block.

        None will be replaced with a proxy block.

        Args:
            blocks: a list of Block instances.
            space: the space in pixels between blocks.
            orientation: orientation of the strip.
            position: position of the strip inside the block.
            background_color: color of the background.
            background_opacity: opacity of the background.
            proxy_block: a block that will replace None values. The height of
                it will be ignored and changed to the max height of the row's
                elements.
            fit_block: if True the element's boundaries will never exceed the block.
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image).
            mode: mode of the background image.
        """
        if orientation not in ["horizontal", "vertical"]:
            raise ValueError(f"Invalid orientation {orientation}.")
        self._proxy_block = proxy_block or Block()
        self.orientation = orientation
        self._blocks = blocks
        self.space = space
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        self.mode = mode
        image = self.strip_image()
        super(Strip, self).__init__(
            image=image,
            position=position,
            fit_block=fit_block,
            keep_proportion=keep_proportion,
            size=size,
            background_color=background_color,
            background_opacity=background_opacity,
            mode=mode,
        )

    @property
    def proxy_block(self):
        """Proxy block."""
        self._proxy_block.size = (self.height, self.height)
        return self._proxy_block

    @property
    def blocks(self):
        """Replace None with proxy blocks."""
        blocks = []
        for block in self._blocks:
            if block.mode != self.mode:
                raise ValueError("All blocks must have the same mode.")
            blocks.append(block) if block is not None else blocks.append(self.proxy_block)
        return blocks

    @property
    def strip_height(self):
        """Height of the row (max of all blocks)."""
        if self.orientation == "horizontal":
            h = max([block.height for block in self.blocks if block is not None])
        else:
            blocks_height = sum([block.height for block in self.blocks])
            extra = (len(self.blocks) - 1) * self.space
            h = blocks_height + extra
        return h

    @property
    def strip_width(self):
        """Width of the row."""
        if self.orientation == "horizontal":
            blocks_width = sum([block.width for block in self.blocks])
            extra = (len(self.blocks) - 1) * self.space
            w = blocks_width + extra
        else:
            w = max([block.width for block in self.blocks if block is not None])
        return w

    @property
    def strip_size(self) -> tuple[int, int]:
        """Size of the strip."""
        return int(self.strip_width), int(self.strip_height)

    def strip_image(self):
        """Create the strip image."""
        background_hex = self.background_color.hex(self.background_opacity)
        im = ImPIL.new(self.mode, self.strip_size, background_hex)
        pos = (0, 0)
        for block in self.blocks:
            i = block.image
            im.paste(i, pos)
            if self.orientation == "horizontal":
                next_width = pos[0] + block.width + self.space
                pos = (next_width, 0)
            else:
                next_height = pos[1] + block.height + self.space
                pos = (0, next_height)
        return im
