"""A gris is just a nested strip."""

import logging

from PIL import Image as ImPIL

from geepillow import colors
from geepillow.blocks import DEFAULT_MODE, Block, ImageBlock, PositionType

logger = logging.getLogger(__name__)


class Grid(ImageBlock):
    """Grid."""

    def __init__(
        self,
        blocks: list[list[Block]],
        x_space: int = 10,
        y_space: int = 10,
        position: tuple | PositionType = "center-center",
        fit_block: bool = True,
        keep_proportion: bool = True,
        size: tuple | None = None,
        background_color: str | colors.Color = "white",
        background_opacity: float = 1,
        mode: str = DEFAULT_MODE,
    ):
        """Grid.

        A vertical strip nested into a horizontal strip.

        Args:
            blocks: a list of Block instances.
            x_space: the space in pixels between blocks.
            y_space: the space in pixels between rows.
            position: position of the strip inside the block.
            background_color: color of the background.
            background_opacity: opacity of the background.
            fit_block: if True the element's boundaries will never exceed the block.
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image).
            mode: mode of the background image.
        """
        self._blocks = blocks
        self._background_color = colors.create(background_color)
        self.x_space = x_space
        self.y_space = y_space
        self.background_opacity = background_opacity
        self.mode = mode
        image = self.grid_image()
        super(Grid, self).__init__(
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
    def blocks(self):
        """Replace None with proxy blocks."""
        blocks = []
        for row in self._blocks:
            row_blocks = []
            for block in row:
                if block is not None and block.mode != self.mode:
                    # raise ValueError("All blocks must have the same mode.")
                    logger.warning(
                        f"Not all blocks have the same mode. Found {block.mode} and {self.mode}"
                    )
                row_blocks.append(block)
            blocks.append(row_blocks)
        return blocks

    def row_height(self, n_row: int) -> int:
        """Height of the n row.

        Args:
            n_row: the position of the row.
        """
        row = self.blocks[n_row]
        return max([block.height for block in row if block is not None])

    def column_width(self, n_column: int) -> int:
        """Width of the n column.

        Args:
            n_column: the position of the column.
        """
        column_blocks = [row[n_column] for row in self.blocks if len(row) > n_column]
        return max([block.width for block in column_blocks if block is not None])

    @property
    def grid_size(self) -> tuple[int, int]:
        """Size of the grid."""
        height = sum([self.row_height(i) + self.y_space for i in range(len(self.blocks))])
        n_columns = max([len(row) for row in self.blocks])
        width = sum([self.column_width(i) + self.x_space for i in range(n_columns)])
        return int(width), int(height)

    def grid_image(self):
        """Create the grid image."""
        background_hex = self.background_color.hex(self.background_opacity)
        im = ImPIL.new(self.mode, self.grid_size, background_hex)
        pos = (0, 0)
        for n_row, row in enumerate(self.blocks):
            for n_col, block in enumerate(row):
                i = block.image
                im.paste(i, pos)
                next_width = pos[0] + self.column_width(n_col) + self.x_space
                # y position is the same for all blocks in the same row (pos[1])
                pos = (next_width, pos[1])
            next_height = pos[1] + self.row_height(n_row) + self.y_space
            pos = (0, next_height)
        return im
