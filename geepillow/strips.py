# coding=utf-8
import ee
import geetools
from PIL import ImageFont, Image
from . import fonts, helpers, blocks, colors, eeimage
import os
from typing import Union, Optional
import json


class SimpleStrip:
    MODE = "RGBA"

    def __init__(self, images: list,
                 background_color: Union[str, colors.Color] = colors.color_from_string("white"),
                 background_opacity: int = 0,
                 y_space: int = 10,
                 x_space: int = 15,
                 ):
        self._images = images  # 2D array of images
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.x_space = x_space
        self.y_space = y_space

    @property
    def images(self):
        max_cols = max([len(l) for l in self._images])
        n_rows = len(self._images)
        empty = [[None]*max_cols for _ in range(n_rows)]
        for y, row in enumerate(self._images):
            for x, col in enumerate(row):
                empty[y][x] = col
        return empty

    @property
    def n_columns(self):
        return len(self.images[0])

    @property
    def n_rows(self):
        return len(self.images)

    def row_size(self, row: int) -> int:
        """Size in pixels of given row"""
        rowi = self.images[row]
        h = max([i.size[1] for i in rowi if i is not None])
        return h

    def column_size(self, column: int) -> int:
        """Size in pixels of given column"""
        coli = [row[column] for row in self.images]
        w = max([i.size[0] for i in coli if i is not None])
        return w

    @property
    def width(self):
        widths = []
        extra = self.x_space * (self.n_columns - 1)
        for row in self.images:
            w = sum(i.size[0] for i in row if i is not None)
            widths.append(w)
        return max(widths) + extra

    @property
    def height(self):
        heights = []
        extra = self.y_space * (self.n_rows - 1)
        for i, _ in enumerate(self.images):
            heights.append(self.row_size(i))
        return sum(heights) + extra

    @property
    def background_size(self):
        return (self.width, self.height)

    @property
    def background_image(self):
        background_hex = self.background_color.hex(self.background_opacity)
        im = Image.new(self.MODE, self.background_size, background_hex)
        return im

    def position(self, x: int, y: int) -> tuple:
        posx= sum([self.column_size(i) for i in range(x)]) + self.x_space * x
        posy = sum([self.row_size(i) for i in range(y)]) + self.y_space * y
        return (posx, posy)

    @property
    def image(self):
        background = self.background_image
        for y, row in enumerate(self.images):
            for x, im in enumerate(row):
                if im is not None:
                    pos = self.position(x, y)
                    background.paste(im, pos)
        return background

    @classmethod
    def from_image_list(cls, images: list, n_columns: int, **kwargs):
        """Create an Image Strip from a list of images"""
        n_rows = len(images) // n_columns
        if len(images) % n_columns > 0:
            n_rows += 1

        final = []
        # Create the 2D array
        array = [[None] * n_columns for _ in range(n_rows)]

        # Fill the 2D array with the elements from the input list
        index = 0
        for row in range(n_rows):
            for col in range(n_columns):
                if index < len(images):
                    array[row][col] = images[index]
                index += 1

        return cls(array, **kwargs)


class SimpleEECollectionStrip(SimpleStrip):
    def __init__(self,
                 collection: ee.ImageCollection,
                 n_columns: int,
                 image_size: tuple,
                 vis_params: Optional[dict] = None,
                 scale: Optional[int] = None,
                 region: Optional[Union[ee.Geometry, ee.Feature]] = None,
                 overlay: Optional[Union[ee.FeatureCollection, ee.Feature, ee.Geometry]] = None,
                 overlay_style: Optional[dict] = None,
                 properties: Optional[dict] = None,
                 font: Optional[fonts.ImageFont] = None,
                 text_color: Optional[colors.Color] = None,
                 unique_id_property: Optional[str] = None
                 ):
        self.collection = collection
        self.image_size = image_size
        self.vis_params = vis_params
        self.scale = scale
        self.region = region
        self.overlay = overlay
        self.overlay_style = overlay_style
        self.properties = properties
        self.unique_id_property = unique_id_property or "system:index"
        self.font = font
        self.text_color = text_color
        self._fetched_images = None
        self._fetched_properties = None
        self._image_ids = None

        # image to init super


    @property
    def image_ids(self) -> list:
        """Unique ids of each image in the collection"""
        if self._image_ids is None:
            ids = self.collection.aggregate_array(self.unique_id_property).getInfo()
            self._image_ids = ids
        return self._image_ids

    @property
    def fetched_images(self) -> dict:
        """A dict of PIL images fetched from GEE --> {unique_id: image}"""
        if self._fetched_images is None:
            images = {}
            for iid in self.image_ids:
                image = self.collection.filter(ee.Filter.eq(self.unique_id_property, iid)).first()
                fetched = eeimage.from_image(
                    image,
                    self.image_size,
                    self.vis_params,
                    self.scale,
                    self.region,
                    self.overlay,
                    self.overlay_style
                )
                images[iid] = fetched
            self._fetched_images = images
        return self._fetched_images

    @property
    def fetched_properties(self) -> dict:
        if self._fetched_properties is None and self.properties is not None:
            properties = {}
            for iid in self.image_ids:
                image = self.collection.filter(ee.Filter.eq(self.unique_id_property, iid)).first()
                props = image.toDictionary(self.properties).getInfo()
                properties[iid] = props
            self._fetched_properties = properties
        return self._fetched_properties

    def _images_to_init(self):
        """Compute the image to init super class"""
        if self.fetched_properties is None:
            imlist = self.fetched_images.values()
            return helpers.array_from_list(imlist, self.n_columns)
        else:
            images = self.fetched_images
            imlist = []
            properties = self.fetched_properties
            proplist = []
            for iid, image in images.items():
                imlist.append(image)
                property = properties.get(iid, {})
                propstr = json.dumps(property)
                block = blocks.TextBlock(
                    propstr,
                    font=self.font,
                    text_color=self.text_color
                )
                proplist.append(block)




class ImageStrip:
    """ Create an image strip """
    def __init__(
            self,
            images: list,
            column_width: int = 500,
            row_height: int = 500,
            n_columns: int = 10,
            descriptions: Optional[list] = None,
            descriptions_background_color: Union[str, colors.Color] = colors.color_from_string("white"),
            descriptions_background_opacity: int = 0,
            descriptions_font: ImageFont = fonts.opensans_regular(12),
            descriptions_text_color: Union[str, colors.Color] = colors.color_from_string("black"),
            title: Optional[str] = None,
            title_size: int = 30,
            title_font: ImageFont = fonts.opensans_regular(18),
            title_color: Union[str, colors.Color] = colors.color_from_string("black"),
            background_color: Union[str, colors.Color] = colors.color_from_string("white"),
            background_opacity: int = 0,
            y_space: int = 10,
            x_space: int = 15,
            fit_block: bool = True,
            keep_proportion: bool = True
    ):
        """Image strip.

        Args:
            images: list of PIL images
        """
        self.images = images
        self.column_width = column_width
        self.row_height = row_height
        self.n_columns = n_columns
        self.descriptions = descriptions
        self.descriptions_background_color = descriptions_background_color
        self.descriptions_background_opacity = descriptions_background_opacity
        self.descriptions_font = descriptions_font
        self.descriptions_text_color = descriptions_text_color
        self.title = title
        self.title_size = title_size
        self.title_font = title_font
        self.title_color = title_color
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.x_space = x_space
        self.y_space = y_space
        self.fit_block = fit_block
        self.keep_proportion = keep_proportion

    @property
    def image_blocks(self) -> list:
        """List of ImageBlock"""
        make_block = lambda i: blocks.ImageBlock(
            i, self.fit_block, self.keep_proportion,
            background_color=self.background_color,
            background_opacity=self.background_opacity
        )
        return [make_block(i) for i in self.images]

    @property
    def description_blocks(self) -> list:
        """List of TextBlock for descriptions"""
        make_block = lambda txt: blocks.TextBlock(
            txt, self.descriptions_font, self.descriptions_text_color,
            y_space=self.y_space
        )
        final = [make_block(txt) for i in self.descriptions] if self.descriptions else []
        return final



class ImageStrip2:
    """ Create an image strip """
    def __init__(self, extension="png",
                 body_size: int = 20,
                 title_size: int = 30,
                 font: ImageFont = fonts.opensans_regular(12),
                 background_color: Union[str, colors.Color] = colors.color_from_string("white"),
                 background_opacity: int = 0,
                 title_color: Union[str, colors.Color] = colors.color_from_string("black"),
                 body_color: Union[str, colors.Color] = colors.color_from_string("red"),
                 body_opacity: int = 1,
                 general_width: int = 0,
                 general_height: int = 0,
                 y_space: int = 10,
                 x_space: int = 15,
                 description: Optional[str] = None
                 ):
        """
        :Opcionals:

        :param extension: Extension. Default: png
        :type extension: str
        :param body_size: Body size. Defaults to 20
        :type body_size: int
        :param title_size: Title's font size. Defaults to 30
        :type title_size: int
        :param font: Font for all texts. defaults to "DejaVuSerif.ttf"
        :type font: str
        :param background_color: Background color. defaults to "white"
        :type background_color: str
        :param title_color: Title's font color. defaults to "black"
        :type title_color: str
        :param body_color: Body's text color. defaults to "red"
        :type body_color:  str
        :param general_width: defaults to 0
        :type general_width: int
        :param general_height: defaults to 0
        :type general_height: int
        :param y_space: Space between lines or rows. defaults to 10
        :type y_space: int
        :param x_space: Space between columns. defaults to 15
        :type x_space: int
        :param description: Description that will go beneath the title
        :type description: str
        """
        self.extension = extension

        self.body_size = body_size
        self.title_size = title_size
        self.description_size = title_size
        self.font = font
        self.background_color = background_color
        self.background_opacity = background_opacity
        self.title_color = title_color
        self.body_color = body_color
        self.general_width = general_width
        self.general_height = general_height
        self.y_space = y_space
        self.x_space = x_space

        if not self.font:
            self.body_font = fonts.provided(self.body_size)
            self.title_font = fonts.provided(self.title_size)
            self.description_font = fonts.provided(self.description_size)
        else:
            self.body_font = ImageFont.truetype(self.font, self.body_size)
            self.title_font = ImageFont.truetype(self.font, self.title_size)
            self.description_font = ImageFont.truetype(self.font,
                                                       self.description_size)

    @staticmethod
    def unpack(doublelist):
        return [y for x in doublelist for y in x]

    def fromList(self, image_list, name=None, name_list=None, vis_params=None,
                 region=None, split_at=4, image_size=(500, 500),
                 description_list=None, images_folder=None, check=True,
                 download_images=False, save=True, folder=None,
                 overlay=None, overlay_style=None):
        """ Download every image and create the strip

        :param image_list: Satellite Images (not PIL!!!!!!)
        :type image_list: list of ee.Image
        :param name_list: Names for the images. Must match imlist
        :type name_list: list of str
        :param description_list: list of descriptions for every image. Optional
        :type description_list: list of str
        :param vis_params: Visualization parameters
        :type vis_params: dict
        :param region: coordinate list. Optional
        :type region: list
        :param folder: folder to downlaod files. Do not use '/' at the end
        :type folder: str
        :param check: Check if file exists, and if it does, omits the downlaod
        :type check: bool

        :return: A file with the name passed to StripImage() in the folder
            passed to the method. Opens the generated file
        """
        if isinstance(image_list, ee.List):
            image_list = helpers.listEE2list(image_list, 'Image')

        if region:
            region = region.bounds()

        description_list = description_list or [None]*len(image_list)
        name_list = name_list or [None]*len(image_list)

        ilist = helpers.split(image_list, split_at)
        nlist = helpers.split(name_list, split_at)
        dlist = helpers.split(description_list, split_at)

        final_list = []

        for imgs, names, descs in zip(ilist, nlist, dlist):
            row_list = []
            for image, iname, desc in zip(imgs, names, descs):

                if download_images:
                    if images_folder:
                        path = os.path.join(os.getcwd(), images_folder)
                    else:
                        if name:
                            path = os.path.join(os.getcwd(), name)
                        else:
                            path = os.getcwd()
                    if not os.path.exists(path):
                        os.mkdir(path)
                else:
                    path = None

                imgblock = blocks.EeImageBlock(
                    image, vis_params, region, check=check, name=iname,
                    extension=self.extension, dimensions=image_size,
                    download=download_images, path=path, overlay=overlay,
                    overlay_style=overlay_style)
                blocklist = [[imgblock]]

                # IMAGE NAME BLOCK
                if iname:
                    textblock = blocks.TextBlock(
                        iname,
                        color=self.body_color,
                        background_color=self.background_color,
                        font=self.body_font)

                    blocklist.append([textblock])

                # DESCRIPTION
                if desc:
                    descblock = blocks.TextBlock(
                        desc,
                        color=self.body_color,
                        background_color=self.background_color,
                        font=self.description_font)
                    blocklist.append([descblock])

                # FINAL CELL BLOCK
                block = blocks.GridBlock(
                    blocklist,
                    background_color=self.background_color,
                    x_space=self.x_space,
                    y_space=self.y_space)

                row_list.append(block)
            final_list.append(row_list)

        # TITLE
        if name:
            title_tb = blocks.TextBlock(
                name,
                color=self.title_color,
                background_color=self.background_color,
                font=self.font,
                font_size=self.title_size)

            final_list.insert(0, [title_tb])

        grid = blocks.GridBlock(
            final_list,
            background_color=self.background_color,
            x_space=self.x_space,
            y_space=self.y_space)

        i = grid.image()

        if save:
            stripname = '{}.{}'.format(name, self.extension)
            local = os.getcwd()
            if not folder:
                path = os.path.join(local, stripname)
            else:
                path = os.path.join(local, folder, stripname)

            i.save(path)

        return i

    def fromCollection(self, collection, title=None, name='{id}',
                       description=None, date_pattern=None, **kwargs):
        """ Create an image strip from a collection """
        collist = collection.toList(collection.size())
        # FILL NAME LIST
        namelist = collist.map(lambda img: geetools.utils.makeName(
            ee.Image(img), name, date_pattern))
        namelist = namelist.getInfo()
        params = dict(name=title, name_list=namelist)
        # FILL DESCRIPTION
        if description:
            desclist = collist.map(lambda img: geetools.utils.makeName(
                ee.Image(img), description, date_pattern))
            desclist = desclist.getInfo()
            params['description_list'] = desclist

        kwargs.update(params)
        return self.fromList(collist, **kwargs)
