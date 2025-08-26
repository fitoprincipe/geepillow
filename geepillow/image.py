"""image module."""

from io import BytesIO
from typing import Any

import ee
import requests
from PIL import Image

from geepillow import colors


def from_eeimage(
    image: ee.Image,
    dimensions: tuple | int,
    viz_params: dict | None = None,
    scale: float | None = None,
    region: ee.Geometry | ee.Feature | None = None,
    overlay: ee.FeatureCollection | ee.Feature | ee.Geometry | None = None,
    overlay_style: dict | None = None,
    style_property: str | None = None,
) -> Image:
    """Create a Pillow Image from an ee.Image.

    Args:
        image: the ee.Image
        dimensions: dimensions of the image, in pixels. If only one number is passed, it is used as the maximum, and
            the other dimension is computed by proportional scaling.
        viz_params: dict with visualization parameters. Admits the following keys:
            - bands: a list of the 3 bands that will represent R G B, or one band that will work with palette.
            - min: the minimum value.
            - max: the maximum value.
            - palette: a list of colors to use as a palette. Will only work with one single band.
        scale: spatial resolution of the image. If None it'll use the image scale.
        region: the region to extract the image from. If None it'll use the boundaries of the image.
        overlay: a vector layer to overlay on top of the image.
        overlay_style: style of the vector layer to overlay.
        style_property: A per-feature property expected to contain a dictionary. Values in the dictionary override any
            default values for that feature.
    """
    viz_params = viz_params or dict(min=0, max=1)
    overlay_style = overlay_style or dict(width=2, fillColor=colors.create("white").hex(0))
    if style_property is not None:
        overlay_style["styleProperty"] = style_property

    if scale is not None:
        proj = image.select([0]).projection().atScale(scale)
        image = image.reproject(proj)

    if isinstance(overlay, ee.Geometry):
        overlay = ee.FeatureCollection([ee.Feature(overlay)])
    elif isinstance(overlay, ee.Feature):
        overlay = ee.FeatureCollection([overlay])

    if overlay is not None:
        overlay_image = ee.Image(overlay.style(**overlay_style))
        source = image.visualize(**viz_params)
        viz_image = source.blend(overlay_image)
    else:
        viz_image = image.visualize(**viz_params)

    viz: dict[str, Any] = {
        "bands": "vis-red,vis-green,vis-blue",
        "min": "0,0,0",
        "max": "255,255,255",
    }
    viz.update({"format": "png", "region": region, "dimensions": dimensions})
    url = viz_image.getThumbURL(viz)
    raw = requests.get(url)
    return Image.open(BytesIO(raw.content))
