# coding=utf-8
import ee
import geetools
from PIL import ImageFont
from . import fonts, helpers, blocks
import os


class ImageStrip(object):
    """ Create an image strip """
    def __init__(self, extension="png", **kwargs):
        """
        :Opcionals:

        :param extension: Extension. Default: png
        :type extension: str
        :param body_size: Body size. Defaults to 18
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

        self.body_size = kwargs.get("body_size", 20)
        self.title_size = kwargs.get("title_size", 30)
        self.description_size = kwargs.get("title_size", 15)
        self.font = kwargs.get("font")
        self.background_color = kwargs.get("background_color", "white")
        self.title_color = kwargs.get("title_color", "black")
        self.body_color = kwargs.get("body_color", "black")
        self.general_width = kwargs.get("general_width", 0)
        self.general_height = kwargs.get("general_height", 0)
        self.y_space = kwargs.get("y_space", 10)
        self.x_space = kwargs.get("x_space", 15)

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
                 download_images=False, save=True, folder=None):
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
            region = geetools.tools.geometry.getRegion(region, True)

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
                    download=download_images, path=path)
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
