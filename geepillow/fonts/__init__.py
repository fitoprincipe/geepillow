import os
from PIL import ImageFont
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import io

URL_FONT = 'http://db.onlinewebfonts.com/t/8050e6017c3b848b20a6324507cfba88.ttf'


def join(name):
    """ join helper """
    return os.path.join(os.getcwd(), name)


def provided(size):
    """ Get font from URL """
    b = urllib2.urlopen(URL_FONT)
    font_file = io.BytesIO(b.read())
    return ImageFont.truetype(font_file, size)
