"""Block for Google Earth Engine images and image collections."""

from __future__ import annotations

import math
from logging import getLogger
from typing import Any, Literal

import ee
import geetools  # noqa: F401

from geepillow import fonts
from geepillow.blocks import DEFAULT_MODE, Block, FontType, ImageBlock, PositionType, TextBlock
from geepillow.colors import Color
from geepillow.grids import Grid
from geepillow.image import from_eeimage

logger = getLogger(__name__)

TextPositionType = Literal["top", "bottom"]

DEFAULT_GRID_FONT = fonts.opensans_bold(24)


class EEImageBlock(ImageBlock):
    """EEImageBlock."""

    def __init__(
        self,
        ee_image: ee.Image,
        viz_params: dict | None = None,
        dimensions: tuple | int = Block.DEFAULT_SIZE,
        scale: int | None = None,
        region: ee.Geometry | ee.Feature | None = None,
        overlay: ee.FeatureCollection | ee.Feature | ee.Geometry | None = None,
        overlay_style: dict | None = None,
        position: tuple | PositionType = "center-center",
        fit_block: bool = True,
        keep_proportion: bool = True,
        size: tuple | None = None,
        background_color: str | Color = "white",
        background_opacity: float = 1,
        mode: str = DEFAULT_MODE,
    ):
        """EEImageBlock.

        By default, the size of the image matches the size of the block.

        Args:
            ee_image: Earth Engine image.
            viz_params: Visualization parameters.
            dimensions: dimensions of the image, in pixels. If only one number is passed, it is used as the maximum, and
                the other dimension is computed by proportional scaling.
            scale: spatial resolution.
            region: region of interest to "clip" the image to.
            overlay: a feature collection to overlay on top of the image.
            overlay_style: style of the overlay.
            position: position of the image inside the block.
            fit_block: if True the element's boundaries will never exceed the block.
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image). If None it will be taken from the dimensions of the image.
            background_color: color of the background.
            background_opacity: opacity of the background.
            mode: mode of the background image
        """
        self.ee_image = ee_image
        self.viz_params = viz_params or dict(min=0, max=1)
        self.dimensions = dimensions
        self.region = region
        self.overlay = overlay
        self.overlay_style = overlay_style
        self.scale = scale
        if size is None and isinstance(dimensions, (int, float)):
            size = (dimensions, dimensions)
        elif isinstance(dimensions, (tuple, list)):
            size = dimensions
        image = from_eeimage(
            image=ee_image,
            dimensions=self.dimensions,
            viz_params=self.viz_params,
            scale=self.scale,
            region=self.region,
            overlay=overlay,
            overlay_style=overlay_style,
        )
        super(EEImageBlock, self).__init__(
            image=image,
            position=position,
            fit_block=fit_block,
            keep_proportion=keep_proportion,
            size=size,
            background_color=background_color,
            background_opacity=background_opacity,
            mode=mode,
        )


class EEImageCollectionGrid(Grid):
    """A Grid for ImageCollections."""

    def __init__(
        self,
        collection: ee.ImageCollection,
        viz_params: dict | None = None,
        scale: int | None = None,
        region: ee.Geometry | ee.Feature | None = None,
        text_pattern: str | None = None,
        text_position: TextPositionType = "bottom",
        font: str | FontType = DEFAULT_GRID_FONT,
        overlay: ee.FeatureCollection | ee.Feature | ee.Geometry | None = None,
        overlay_style: dict | None = None,
        x_space: int = 10,
        y_space: int = 10,
        n_columns: int | None = None,
        n_rows: int | None = None,
        image_dimensions: tuple | int | None = None,
        dimensions: tuple = (3300, 2250),
        image_position: tuple | PositionType = "center-center",
        text_inner_position: tuple | PositionType = "center-center",
        position: tuple | PositionType = "center-center",
        fit_block: bool = True,
        keep_proportion: bool = True,
        size: tuple | None = None,
        background_color: str | Color = "white",
        background_opacity: float = 1,
        mode: str = DEFAULT_MODE,
    ):
        """A grid for image collections.

        This class is designed for Image Collection with overlapping images.

        If n_columns is not None and n_rows is None, the number of rows will be computed
        using the number of images. Same the other way around. If both are None, n_columns
        will be set to 3.

        Args:
            collection: Earth Engine image collection.
            n_columns: number of columns.
            n_rows: number of rows.
            viz_params: Visualization parameters.
            scale: spatial resolution.
            text_pattern: A text pattern to include in the position indicated by text_position param.
                Properties of the image can be used inside this text following this guide:
                https://geetools.readthedocs.io/en/stable/autoapi/geetools/ee_string/StringAccessor.format.html
            text_position: the position of the text block.
            font: font to use. The size the font is included in this parameter.
            region: region of interest to "clip" each image to. If None it uses the geometry of each image.
            overlay: a feature collection to overlay on top of the image.
            overlay_style: style of the overlay.
            image_dimensions: dimensions of the image, in pixels. If only one number is passed, it is used as the
                maximum, and the other dimension is computed by proportional scaling.
            dimensions: dimensions of the grid image in pixels. The default value corresponds to the size of a Letter
                at 300 DPI (landscape orientation).
            image_position: position of the image inside its block.
            text_inner_position: position of the text inside its block.
            position: position of the grid inside its block.
            fit_block: if True the element's boundaries will never exceed the block.
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image).
            background_color: color of the background.
            background_opacity: opacity of the background.
            mode: mode of the background image
            x_space: space on the x axis.
            y_space: space on the y axis.
        """
        self.collection = collection
        if n_columns is None and n_rows is None and image_dimensions is None:
            raise ValueError(
                "You need to pass at least one of: `n_columns`, `n_rows` or `image_dimensions`."
            )
        if image_dimensions is not None and isinstance(image_dimensions, (int, float)):
            image_dimensions = (image_dimensions, image_dimensions)
        self.viz_params = viz_params or dict(min=0, max=1)
        self.dimensions = dimensions
        self.scale = scale
        self.region = region
        self.overlay = overlay
        self.overlay_style = overlay_style
        self.text_pattern = text_pattern
        self.text_position = text_position
        self.image_position = image_position
        self.text_inner_position = text_inner_position
        self.font = font
        self.x_space = x_space
        self.y_space = y_space
        self._image_dimensions = image_dimensions
        self._n_rows = n_rows
        self._n_columns = n_columns
        self._image_ids = None

        blocks = self.make_blocks()
        super().__init__(
            blocks=blocks,
            x_space=x_space,
            y_space=y_space,
            position=position,
            size=size or dimensions,
            fit_block=fit_block,
            keep_proportion=keep_proportion,
            background_color=background_color,
            background_opacity=background_opacity,
            mode=mode,
        )

    @property
    def image_ids(self):
        """Ids of all the images in the collection."""
        if self._image_ids is None:
            self._image_ids = self.collection.aggregate_array("system:index").getInfo()
        return self._image_ids

    @property
    def image_dimensions(self):
        """Dimensions of each image."""
        if self._image_dimensions is not None:
            image_dimensions = self._image_dimensions
        else:
            # compute image dimensions using the number of columns and the dimensions of the grid
            # compute max width
            x_dimension = self.dimensions[0]
            spaces = self.x_space * (self.n_columns - 1)
            width = math.floor((x_dimension - spaces) / self.n_columns)
            # compute max height
            y_dimension = self.dimensions[1]
            spaces = self.y_space * (self.n_rows - 1)
            height = math.floor((y_dimension - spaces) / self.n_rows)
            dim = min(width, height)
            image_dimensions = (dim, dim)
        return image_dimensions

    @property
    def n_columns(self) -> int:
        """Number of columns."""
        if self._n_columns is not None:
            return self._n_columns
        elif self._n_rows is not None:
            return math.ceil(len(self.image_ids) / self._n_rows)
        else:
            if self._image_dimensions:
                return math.floor(
                    (self.dimensions[0] + self.x_space) / (self._image_dimensions[0] + self.x_space)
                )
            else:
                return 3

    @property
    def n_last(self) -> int:
        """Number of elements in the last row."""
        return len(self.image_ids) % self.n_columns

    @property
    def n_rows(self):
        """Number of rows."""
        if self._n_rows is not None:
            n_rows = self._n_rows
        else:
            n_rows = int(len(self.image_ids) / self.n_columns)
        if self.n_last > 0:
            n_rows += 1
        return n_rows

    def make_image_block(self, image: ee.Image) -> Block:
        """Make the block for the image and text block if needed."""
        from geepillow.strips import Strip

        image_block = EEImageBlock(
            image,
            self.viz_params,
            self.image_dimensions,
            self.scale,
            self.region,
            self.overlay,
            self.overlay_style,
        )
        if self.text_pattern is None:
            return image_block

        # all properties on the server-side
        properties = image.toDictionary(image.propertyNames())
        formatted = ee.String(self.text_pattern).geetools.format(properties)
        text = formatted.getInfo()
        txt_block = TextBlock(text, self.text_inner_position, font=self.font)
        strip_blocks: list[Any] = (
            [txt_block, image_block] if self.text_position == "top" else [image_block, txt_block]
        )
        return Strip(strip_blocks, self.y_space, "vertical")

    def make_blocks(self) -> list[list[Block]]:
        """Make the list of blocks for the grid."""
        grid_blocks: list[list[Block]] = []
        i = 0
        while i < len(self.image_ids):
            row: list[Block] = []
            if (
                len(grid_blocks) == self.n_rows - 1
                and len(grid_blocks[-1]) == self.n_columns
                and self.n_last > 0
            ):
                columns = range(self.n_last)
            else:
                columns = range(self.n_columns)
            for _ in columns:
                iid = self.image_ids[i]
                eeimage = ee.Image(
                    self.collection.filter(ee.Filter.eq("system:index", iid)).first()
                )
                item_block = self.make_image_block(eeimage)
                row.append(item_block)
                i += 1
            grid_blocks.append(row)
        return grid_blocks
