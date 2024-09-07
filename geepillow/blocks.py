# coding=utf-8
import json

import ee
from typing import Optional, Union, Literal
from . import helpers, fonts, colors
from .colors import Color
from PIL import Image as ImPIL
from PIL import ImageDraw
from PIL.ImageFont import ImageFont, FreeTypeFont, TransposedFont
import os.path
from copy import deepcopy
import requests
from io import BytesIO
import os
import hashlib
import geetools
from pathlib import Path
import numpy as np
from .eeimage import from_image

DEFAULT_FONT = fonts.opensans_regular(12)

font_type = Union[ImageFont, FreeTypeFont, TransposedFont]

position_type = Literal[
    "top-left", "top-center", "top-right", "center-left", "center-center",
    "center-right", "bottom-left", "bottom-center", "bottom-right"
]


class Block:
    """Basic Block"""
    def __init__(self, size: tuple = (500, 500),
                 background_color: Union[str, Color] = 'white',
                 background_opacity: float = 0):
        """Basic Block.

        The background will always be an image that will cover the whole block.
        Then then inner element will be painted on top of the background image.

        This object is mutable. All properties, except "element" can be
        modified.

        Args:
            size: size of the block (width, height). The background image will
                have this size
            background_color: color of the background
            background_opacity: opacity of the background
        """
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        self._size = size or (500, 500)
        self._width = size[0]
        self._height = size[1]

    @property
    def image(self):
        """For basic blocks the image is the background image"""
        return self.background_image()

    @property
    def background_hex(self):
        """Background hex color"""
        return self.background_color.hex(self.background_opacity)

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color: Union[str, Color]):
        self._background_color = colors.create(color)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size: tuple):
        self._size = size
        self._width = size[0]
        self._height = size[1]

    def set_size(self, size: tuple):
        """Set or modify the size of the block"""
        self.size = size

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width
        size = list(self.size)
        size[0] = width
        self._size = tuple(size)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: float):
        self._height= height
        size = list(self.size)
        size[0] = height
        self._size = tuple(size)

    def background_image(self):
        """The background image"""
        im = ImPIL.new("RGBA", self.size, self.background_hex)
        return im

    # def topleft(self):
    #     return self.position
    #
    # def topright(self):
    #     x = self.position[0] + self.width
    #     return x, self.position[1]
    #
    # def bottomleft(self):
    #     y = self.position[1] + self.height
    #     return self.position[0], y
    #
    # def bottomright(self):
    #     x = self.position[0] + self.width
    #     y = self.position[1] + self.height
    #     return x, y


class ImageBlock(Block):
    def __init__(self, image: ImPIL.Image,
                 position: Union[tuple, position_type] = "center-center",
                 fit_block: bool = True,
                 keep_proportion: bool = True,
                 size: Optional[tuple] = None,
                 **kwargs):
        """Image Block for PIL images

        Args:
            image: the image.
            position: position of the image inside the block.
            fit_block: if True the element's boundaries will never exceed the block.
            keep_proportion: keep proportion (ratio) of the image.
            size: size of the block (not the image).
        """
        if size is None:
            size = image.size
        self._image = image  # store the original image
        self._element = image  # this will be modified as needed
        super(ImageBlock, self).__init__(size=size, **kwargs)
        # self._proportion = element.size[0] / element.size[1]
        self.position = position
        self.fit_block = fit_block
        self.keep_proportion = keep_proportion

    @property
    def xy(self):
        """X,Y of the position."""
        x_space = self.width - self._image.width
        y_space = self.height - self._image.height
        options = {
            "top-left": (0, 0),
            "top-center": (x_space / 2 , 0),
            "top-right": (x_space, 0),
            "center-left": (0, y_space / 2),
            "center-center": (x_space / 2, y_space / 2),
            "center-right": (x_space, y_space / 2),
            "bottom-left": (0, y_space),
            "bottom-center": (x_space / 2, y_space),
            "bottom-right": (x_space, y_space)
        }
        if isinstance(self.position, str):
            try:
                pos = options[self.position]
            except KeyError:
                raise KeyError(f"Position '{self.position}' not in {list(options.keys())}")
            return (int(pos[0]), int(pos[1]))
        else:
            return self.position

    def new_size(self):
        if not self.fit_block:
            return self.size
        elw, elh = self._image.size[0], self._image.size[1]
        blockw, blockh = self.size[0], self.size[1]
        posx, posy = self.xy[0], self.xy[1]
        is_widther, is_heigher = (posx + elw) > blockw, (posy + elh) > blockh
        if not self.keep_proportion:
            new_width = blockw - posx if is_widther else elw
            new_height = blockh-posy if is_heigher else elh
        else:
            proportion = self._image.size[0] / self._image.size[1]


    @property
    def element(self) -> ImPIL.Image:
        """The original image will be modified according to size of the block 
        and properties fit_block and keep_proportion"""
        self._element = self._image
        elw, elh = self._element.size[0], self._element.size[1]
        blockw, blockh = self.size[0], self.size[1]
        posx, posy = self.xy[0], self.xy[1]
        is_widther, is_heigher = (posx + elw) > blockw, (posy + elh) > blockh
        if self.fit_block:
            if not self.keep_proportion:
                if is_widther:
                    new_size = (blockw - posx, elh)
                    self._element = self._element.resize(new_size)
                if is_heigher:
                    new_size = (elw, blockh-posy)
                    self._element = self._element.resize(new_size)
            else:
                proportion = self._element.size[0] / self._element.size[1]
                if is_widther:
                    new_width = blockw - posx
                    new_size = (new_width, int(new_width / proportion))
                    self._element = self._element.resize(new_size)
                if (posy + self._element.size[1]) > blockh:
                    new_height = blockh - posy
                    new_size = (int(new_height * proportion), new_height)
                    self._element = self._element.resize(new_size)
        return self._element

    @property
    def image(self) -> ImPIL:
        im = self.background_image()
        im.paste(self.element, self.xy)
        return im

    @classmethod
    def from_file(cls, filename: Union[str, Path], **kwargs):
        filename = Path(filename)
        return cls(ImPIL.open(filename), **kwargs)


class TextBlock(ImageBlock):
    def __init__(self, text: str,
                 position: Union[position_type, tuple] = "center-center",
                 font: Union[ImageFont, str] = DEFAULT_FONT,
                 text_color: Union[str, Color] = 'black',
                 text_opacity: float = 1, font_size: int = 12,
                 background_color: Union[str, Color] = 'white',
                 background_opacity: float = 0,
                 **kwargs):
        self._text = text
        self._text_color = text_color
        self.text_opacity = text_opacity
        self.font_size = font_size
        self._font = fonts.create(font, font_size)
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        image = self.create_text_image()
        kwargs.setdefault("background_color", background_color)
        kwargs.setdefault("background_opacity", background_opacity)
        super(TextBlock, self).__init__(image, position, **kwargs)

    @property
    def text(self) -> str:
        return self._text

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font: Union[ImageFont, str]):
        if isinstance(font, (ImageFont, FreeTypeFont, TransposedFont)):
            self.font_size = font.size
        self._font = fonts.create(font, self.font_size)

    @property
    def text_color(self) -> Color:
        return self._text_color

    @text_color.setter
    def text_color(self, color: Union[str, Color]):
        self._text_color = colors.create(color)

    @property
    def text_height(self) -> int:
        """Calculate height for a multiline text"""
        alist = self.text.split("\n")
        alt = 0
        for line in alist:
            alt += self.font.getbbox(line)[3] + self.font.getbbox(line)[1]
        # return alt
        return int(alt)

    @property
    def text_width(self) -> int:
        """Calculate width for a multiline text"""
        alist = self.text.split("\n")
        widths = []
        for line in alist:
            w = self.font.getbbox(line)[2]
            widths.append(w)
        return int(max(widths))

    def create_text_image(self) -> ImPIL.Image:
        image = ImPIL.new("RGBA", (self.text_width, self.text_height),
                          self.background_hex)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), self.text, font=self.font,
                  fill=self.text_color)
        return image


class EEImageBlock(ImageBlock):
    def __init__(self, ee_image: ee.Image, vis_params: Optional[dict] = None,
                 scale: Optional[int] = None,
                 region: Optional[Union[ee.Geometry, ee.Feature]] = None,
                 overlay: Optional[Union[ee.FeatureCollection, ee.Feature, ee.Geometry]] = None,
                 overlay_style: Optional[dict] = None,
                 properties: Optional[list] = None,
                 properties_style: Optional[dict] = None,
                 size: tuple = (500, 500),
                 background_color: Union[str, Color] = 'white',
                 background_opacity: float = 0,
                 **kwargs):
        self.ee_image = ee_image
        self.vis_params = vis_params or dict(min=0, max=1)
        self.region = region
        if isinstance(overlay, ee.Geometry):
            overlay = ee.FeatureCollection([ee.Feature(overlay)])
        elif isinstance(overlay, ee.Feature):
            overlay = ee.FeatureCollection([overlay])
        self.overlay = overlay
        self.overlay_style = overlay_style or dict(
            width=2,
            fillColor=colors.color_from_string("white").hex(0)
        )
        self.scale = scale
        self.properties = properties
        self.properties_style = properties_style
        self.properties_dict = {}
        self._background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        kwargs.setdefault("size", size)
        image = from_image(ee_image, size, vis_params, scale, region,
                           overlay, overlay_style)
        self.ee_image_pil = image
        self.properties_block = None
        if properties is not None:
            self.properties_dict = ee_image.toDictionary(properties).getInfo()
            style = properties_style or {}
            txt = TextBlock(json.dumps(self.properties_dict, indent=2),
                            size=image.size, **style)
            self.properties_block = txt
            empty = ImPIL.new("RGBA", (txt.width, txt.height*2),
                              self.background_hex)
            empty.paste(image, (0, 0))
            empty.paste(txt.image, (0, image.size[1]))
            image = empty

        super(EEImageBlock, self).__init__(image, **kwargs)




class EEImageBlock2(ImageBlock):
    def __init__(self, ee_image: ee.Image, vis_params: Optional[dict] = None,
                 scale: Optional[int] = None,
                 region: Optional[Union[ee.Geometry, ee.Feature]] = None,
                 path: Optional[Union[str, Path]] = None,
                 overlay: Optional[Union[ee.FeatureCollection, ee.Feature, ee.Geometry]] = None,
                 overlay_style=None, **kwargs):
        self.ee_image = ee_image
        self.vis_params = vis_params or dict(min=0, max=1)
        self.region = region
        self.path = Path(path) if path is not None else None
        if isinstance(overlay, ee.Geometry):
            overlay = ee.FeatureCollection([ee.Feature(overlay)])
        elif isinstance(overlay, ee.Feature):
            overlay = ee.FeatureCollection([overlay])
        self.overlay = overlay
        self.overlay_style = overlay_style or dict(
            width=2,
            fillColor=colors.color_from_string("white").hex(0)
        )
        self.scale = scale
        self._url = None
        self._pil_image = None
        self._size = kwargs.pop("size", (500, 500))
        super(EEImageBlock2, self).__init__(self.pil_image, **kwargs)

    @property
    def visual_image(self):
        """The visual image. 8 bits bands: vis-red, vis-green, vis-blue.

        If an overlay geometry is passed, it'll be pained on top of the image
        """
        eeimage = self.ee_image
        if self.scale is not None:
            eeimage = eeimage.reproject(eeimage.select([0]).projection().atScale(self.scale))
        if self.overlay is not None:
            overlay_image = ee.Image(self.overlay.style(**self.overlay_style))
            source = eeimage.visualize(**self.vis_params)
            image = source.blend(overlay_image)
        else:
            image = eeimage.visualize(**self.vis_params)
        return image

    @staticmethod
    def format_dimensions(dimensions):
        x = dimensions[0]
        y = dimensions[1]
        if x and y:
            return "x".join([str(d) for d in dimensions])
        elif x:
            return str(x)
        else:
            return str(y)

    @property
    def url(self):
        if not self._url:
            vis = {"bands": "vis-red,vis-green,vis-blue", "min": "0,0,0", "max": "255,255,255"}
            vis.update({
                'format': 'png',
                'region': self.region,
                'dimensions': self.format_dimensions(self.size)
            })
            url = self.visual_image.getThumbURL(vis)
            self._url = url
        return self._url

    @property
    def pil_image(self):
        if not self._pil_image:
            if self.path is None:
                raw = requests.get(self.url)
                self._pil_image = ImPIL.open(BytesIO(raw.content))
            else:
                if self.path.exists():
                    self._pil_image = ImPIL.open(self.path)
                else:
                    file = helpers.download_file(self.url, self.path)
                    self._pil_image = ImPIL.open(file)
        return self._pil_image


class RowBlock:
    def __init__(self, blocklist: list, x_space: float = 10,
                 background_color: Union[str, Color] = 'white',
                 background_opacity: float = 0, proxy_block: Block = Block()):
        """Row Block. A list of blocks that behave like a block.

        None will be replaced with a proxy block.

        Args:
            blocklist: a list of Block instances.
            x_space: the space in pixels between blocks.
            background_color: color of the background.
            background_opacity: opacity of the background.
            proxy_block: a block that will replace None values. The height of
                it will be ignored and changed to the max height of the row's
                elements. The width will also be ignored and changed to
        """
        self._proxy_block = proxy_block
        self.blocklist = blocklist
        self.x_space = x_space
        self.background_color = colors.create(background_color)
        self.background_opacity = background_opacity

    @property
    def height(self):
        "Height of the row (max of all blocks)"
        h = max([block.height for block in self.blocklist if block is not None])
        return h

    @property
    def proxy_block(self):
        self._proxy_block.size = (self.height, self.height)
        return self._proxy_block

    @property
    def final_blocklist(self):
        """Replace None with proxy blocks"""
        blocks = []
        for block in self.blocklist:
            if block is not None:
                blocks.append(block)
            else:
                blocks.append(self.proxy_block)
        return blocks

    @property
    def width(self):
        """Width of the row"""
        blocks_width = sum([block.width for block in self.final_blocklist])
        extra = (len(self.blocklist) - 1) * self.x_space
        return blocks_width + extra

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def image(self):
        background_hex = self.background_color.hex(self.background_opacity)
        im = ImPIL.new("RGBA", self.size, background_hex)
        pos = (0, 0)
        for block in self.final_blocklist:
            i = block.image
            im.paste(i, pos)
            nextwidth = pos[0] + block.width + self.x_space
            pos = (nextwidth, 0)
        return im


class GridBlock:
    def __init__(self, blocklist: list, x_space: float = 10,
                 y_space: float = 10,
                 background_color: Union[str, Color] = 'white',
                 background_opacity: float = 0,
                 proxy_block: Block = Block()):
        """A grid container for blocks.

        Each row has its own hight and width. None will be replaced with a
        proxy block

        Args:
            blocklist: a list of lists with Blocks (or child).
            x_space: the space between blocks in the x axis.
            y_space: the space between blocks in the y axis.
            background_color: color of the background. Defaults to white.
            background_opacity: opacity of the background. Default to transparent.
        """
        self.blocklist = blocklist
        self.x_space = x_space
        self.y_space = y_space
        self.background_color = colors.create(background_color)
        self.background_opacity = background_opacity
        self.proxy_block = proxy_block

    @property
    def rows(self) -> list:
        final = []
        for row in self.blocklist:
            if not isinstance(row, RowBlock):
                row = RowBlock(
                    row, self.x_space, self.background_color,
                    self.background_opacity, self.proxy_block
                )
            final.append(row)
        return final

    @property
    def width(self):
        """Width of the grid"""
        w = max([row.width for row in self.rows])
        return w

    @property
    def height(self):
        """Hieght of the grid"""
        h = sum([row.height for row in self.rows])
        extra = (len(self.rows) - 1) * self.y_space
        return h + extra

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def image(self):
        background_hex = self.background_color.hex(self.background_opacity)
        im = ImPIL.new("RGBA", self.size, background_hex)
        pos = (0, 0)
        for row in self.rows:
            i = row.image
            im.paste(i, pos)
            nextheight = pos[1] + row.height + self.y_space
            pos = (0, nextheight)
        return im

    # @staticmethod
    # def _format_blocklist(blocklist):
    #     """Create an square/rectangular list of lists (array) by filling with
    #     None the missing parts"""
    #     rows = len(blocklist)
    #     cols = max([len(row) for row in blocklist])
    #     # create emtpy array
    #     empty_array = []
    #     for i in range(rows):
    #         empty_array.append([None] * cols)
    #     # fill empty array with data
    #     for row_n, r in enumerate(blocklist):
    #         for col_n, block in enumerate(r):
    #             empty[row_n][col_n] = block
    #     return empty
    #
    # def row_height(self, row: int) -> int:
    #     """Get height of the row"""
    #     r = self.blocklist[row]
    #     h = max([im.height for im in r if im is not None])
    #     return h


class GridBlock2(Block):
    def __init__(self, blocklist: list, x_space: float = 10,
                 y_space: float = 10, **kwargs):
        """A container Block that behaves as a grid.

        Args:
            blocklist: a list of lists with Blocks (or child)
            x_space: the space between blocks in the x axis
            y_space: the space between blocks in the y axis
        """
        super(GridBlock2, self).__init__(**kwargs)
        self.blocklist = self._format_blocklist(blocklist)
        self.x_space = x_space
        self.y_space = y_space

    @staticmethod
    def _format_blocklist(blocklist):
        rows = len(blocklist)
        cols = 0
        for l in blocklist:
            length = len(l)
            cols = length if length > cols else cols

        row = [None]*cols
        empty = []
        for i in range(rows):
            empty.append(deepcopy(row))

        for row_n, r in enumerate(blocklist):
            for col_n, block in enumerate(r):
                empty[row_n][col_n] = block

        return empty

    def get(self, x, y):
        """Get a block given it's coordinates on the grid"""
        return self.blocklist[x][y]

    def row_height(self, row):
        r = self.blocklist[row]
        h = 0
        for im in r:
            imh = im.height if im else 0
            # update h if image height is bigger
            h = imh if imh > h else h
        return h

    def height(self):
        heightlist = []
        for l in self.blocklist:
            h = 0
            for block in l:
                bh = block.height if block else 0
                # update h if image height is bigger
                h = bh if bh > h else h
            heightlist.append(h)
        return sum(heightlist) + ((len(heightlist)-1) * self.y_space)

    def width(self):
        widthlist = []
        for l in self.blocklist:
            w = 0
            for block in l:
                bw = block.width if block else 0
                w += bw
            w = w + ((len(l)-1) * self.x_space)
            widthlist.append(w)
        return max(widthlist)

    @property
    def image(self):
        im = ImPIL.new("RGBA", self.size, self.background_hex)
        nextpos = (0, 0)
        for rown, blist in enumerate(self.blocklist):
            for block in blist:
                if block:
                    i = block.image
                    im.paste(i, nextpos)
                    nextwidth = nextpos[0] + block.width + self.x_space
                    nextpos = (nextwidth, nextpos[1])
            nextpos = (0, nextpos[1] + self.row_height(rown) + self.y_space)
        return im
