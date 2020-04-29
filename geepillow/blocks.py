# coding=utf-8
import ee
from . import helpers, fonts
from PIL import Image as ImPIL
from PIL import ImageDraw, ImageFont
import os.path
from copy import deepcopy
import requests
from io import BytesIO
import os
import hashlib
import geetools


class Block(object):
    """ Basic Block """
    def __init__(self, position=(0, 0), background_color=None):
        self.position = position
        self.background_color = background_color or "#00000000"  # transparent

    def image(self):
        """ Overwrite this method """
        im = ImPIL.new("RGBA", self.size(), self.background_color())
        return im

    def height(self):
        """ Overwrite this method """
        return 0

    def width(self):
        """ Overwrite this method """
        return 0

    def size(self):
        return self.width(), self.height()

    def topleft(self):
        return self.position

    def topright(self):
        x = self.position[0] + self.width()
        return x, self.position[1]

    def bottomleft(self):
        y = self.position[1] + self.height()
        return self.position[0], y

    def bottomright(self):
        x = self.position[0] + self.width()
        y = self.position[1] + self.height()
        return x, y


class TextBlock(Block):
    def __init__(self, text, font=None, color='white', font_size=12,
                 y_space=10, **kwargs):
        super(TextBlock, self).__init__(**kwargs)
        self.text = text
        self.color = color
        self.font_size = font_size
        self.y_space = y_space
        if not isinstance(font, ImageFont.FreeTypeFont):
            if font is None:
                self.font = fonts.provided(self.font_size)
                # self.font = ImageFont.truetype("OpenSans-Regular.ttf",
                #                                self.font_size)
            else:
                self.font = ImageFont.truetype(font, self.font_size)
        else:
            self.font = font

    def image(self):
        """ Return the PIL image """
        image = ImPIL.new("RGBA", self.size(), self.background_color)
        draw = ImageDraw.Draw(image)
        draw.text(self.position, self.text,
                  font=self.font, fill=self.color)
        return image

    def height(self):
        """ Calculate height for a multiline text """
        alist = self.text.split("\n")
        alt = 0
        for line in alist:
            alt += self.font.getsize(line)[1]
        return alt + self.y_space + self.position[1]

    def width(self):
        """ Calculate height for a multiline text """
        alist = self.text.split("\n")
        widths = []
        for line in alist:
            w = self.font.getsize(line)[0]
            widths.append(w)
        return max(widths) + self.position[0]

    def draw(self, image, position=(0, 0)):
        """ Draw the text image into another PIL image """
        im = self.image()
        newi = image.copy()
        newi.paste(im, position, im)
        return newi


class ImageBlock(Block):
    def __init__(self, source, **kwargs):
        """ Image Block for PIL images """
        super(ImageBlock, self).__init__(**kwargs)
        self.source = source

    def height(self):
        return self.source.size[1] + self.position[1]

    def width(self):
        return self.source.size[0] + self.position[0]

    def image(self):
        im = ImPIL.new("RGBA", self.size(), self.background_color)
        im.paste(self.source, self.position)
        return im


class EeImageBlock(Block):
    def __init__(self, source, visParams=None, region=None,
                 download=False, check=True, path=None, name=None,
                 extension=None, dimensions=(500, 500), **kwargs):
        """ Image Block for Earth Engine images """
        super(EeImageBlock, self).__init__(**kwargs)
        self.source = ee.Image(source)
        self.visParams = visParams or dict(min=0, max=1)
        self.dimensions = dimensions
        self.download = download
        self.extension = extension or 'png'
        self.check = check
        self.visual = self.source.visualize(**self.visParams)
        self.name = name

        if region:
            self.region = geetools.tools.geometry.getRegion(region, True)
        else:
            self.region = geetools.tools.geometry.getRegion(self.source, True)

        if download:
            self.path = path or os.getcwd()
            h = hashlib.sha256()
            tohash = self.visual.serialize()+str(self.dimensions)+str(self.region)
            h.update(tohash.encode('utf-8'))
            namehex = h.hexdigest()
            if not name:
                self.name = namehex
            else:
                self.name = '{}_{}'.format(self.name, namehex)
        else:
            self.path = path

        self._pil_image = None
        self._url = None

    @property
    def pil_image(self):
        if not self._pil_image:
            if not self.download:
                raw = requests.get(self.url)
                self._pil_image = ImPIL.open(BytesIO(raw.content))
            else:
                if not os.path.exists(self.path):
                    os.mkdir(self.path)
                filename = '{}.{}'.format(self.name, self.extension)
                fullpath = os.path.join(self.path, filename)
                exist = os.path.isfile(fullpath)
                if self.check and exist:
                    self._pil_image = ImPIL.open(fullpath)
                else:
                    file = helpers.downloadFile(
                        self.url, self.name, self.extension, self.path)
                    self._pil_image = ImPIL.open(file.name)

        return self._pil_image

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
            vis = geetools.utils.formatVisParams(self.visParams)
            vis.update({'format': self.extension, 'region': self.region,
                        'dimensions': self.format_dimensions(self.dimensions)})
            url = self.source.getThumbURL(vis)
            self._url = url

        return self._url

    def height(self):
        return self.pil_image.size[1] + self.position[1]

    def width(self):
        return self.pil_image.size[0] + self.position[0]

    def image(self):
        im = ImPIL.new("RGBA", self.size(), self.background_color)
        im.paste(self.pil_image, self.position)
        return im


class GridBlock(Block):
    def __init__(self, blocklist, x_space=10, y_space=10, **kwargs):
        """ """
        super(GridBlock, self).__init__(**kwargs)
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
        """ Get a block given it's coordinates on the grid """
        return self.blocklist[x][y]

    def row_height(self, row):
        r = self.blocklist[row]
        h = 0
        for im in r:
            imh = im.height() if im else 0
            # update h if image height is bigger
            h = imh if imh > h else h
        return h

    def height(self):
        heightlist = []
        for l in self.blocklist:
            h = 0
            for block in l:
                bh = block.height() if block else 0
                # update h if image height is bigger
                h = bh if bh > h else h
            heightlist.append(h)
        return sum(heightlist) + ((len(heightlist)-1) * self.y_space)

    def width(self):
        widthlist = []
        for l in self.blocklist:
            w = 0
            for block in l:
                bw = block.width() if block else 0
                w += bw
            w = w + ((len(l)-1) * self.x_space)
            widthlist.append(w)
        return max(widthlist)

    def image(self):
        im = ImPIL.new("RGBA", self.size(), self.background_color)
        nextpos = (0, 0)
        for rown, blist in enumerate(self.blocklist):
            for block in blist:
                if block:
                    i = block.image()
                    im.paste(i, nextpos)
                    nextwidth = nextpos[0] + block.width() + self.x_space
                    nextpos = (nextwidth, nextpos[1])
            nextpos = (0, nextpos[1] + self.row_height(rown) + self.y_space)
        return im
