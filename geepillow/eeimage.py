from PIL import Image
import ee
from typing import Optional, Union
from . import colors
import requests
from io import BytesIO


def from_image(
        image: ee.Image,
        dimensions: tuple,
        vis_params: Optional[dict] = None,
        scale: Optional[int] = None,
        region: Optional[Union[ee.Geometry, ee.Feature]] = None,
        overlay: Optional[Union[ee.FeatureCollection, ee.Feature, ee.Geometry]] = None,
        overlay_style: Optional[dict] = None
):
    """Create a Pillow Image from an ee.Image

    Args:
        image: the ee.Image
        dimensions: dimensions of the image in pixels.
        vis_params: dict with visualization parameters. Admits the following keys:
            - bands: a list of the 3 bands that will represent R G B, or one band that will work with palette.
            - min: the minimum value.
            - max: the maximum value.
            - palette: a list of colors to use as a palette. Will only work with one single band.
        scale: spatial resolution of the image. If None it'll use the image scale.
        region: the region to extract the image from. If None it'll use the boudaries of the image.
        overlay: a vector layer to overlay on top of the image
        overlay_style: style of the vector layer to overlay
    """
    vis_params = vis_params or dict(min=0, max=1)
    overlay_style = overlay_style or dict(
        width=2,
        fillColor=colors.color_from_string("white").hex(0)
    )
    if scale is not None:
        image = image.reproject(image.select([0]).projection().atScale(scale))

    if isinstance(overlay, ee.Geometry):
        overlay = ee.FeatureCollection([ee.Feature(overlay)])
    elif isinstance(overlay, ee.Feature):
        overlay = ee.FeatureCollection([overlay])

    if overlay is not None:
        overlay_image = ee.Image(overlay.style(**overlay_style))
        source = image.visualize(**vis_params)
        visimage = source.blend(overlay_image)
    else:
        visimage = image.visualize(**vis_params)

    vis = {"bands": "vis-red,vis-green,vis-blue", "min": "0,0,0", "max": "255,255,255"}
    vis.update({
        'format': 'png',
        'region': region,
        'dimensions': dimensions
    })
    url = visimage.getThumbURL(vis)
    raw = requests.get(url)
    return Image.open(BytesIO(raw.content))
