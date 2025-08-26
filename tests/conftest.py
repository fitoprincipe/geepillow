"""Pytest session configuration."""

from io import BytesIO
from pathlib import Path

import ee
import pytest
import pytest_gee
from PIL import Image  # Add this import for type hinting


def pytest_configure() -> None:
    """Initialize earth engine according to the environment."""
    pytest_gee.init_ee_from_service_account()


class PILImageRegression:
    """A helper class to encapsulate image regression checking."""

    def __init__(self, image_regression_fixture):
        """
        Initializes the checker with the image_regression fixture.

        Args:
            image_regression_fixture: The pytest-image-regression fixture.
        """
        self._image_regression = image_regression_fixture

    def check(self, image: Image.Image):
        """
        Converts a PIL image to bytes and performs a regression check.

        Args:
            image (PIL.Image.Image): The PIL image to check.
        """
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        self._image_regression.check(buffer.read())


@pytest.fixture
def pil_image_regression(image_regression):
    """
    A fixture that returns an ImageChecker instance.

    This provides a convenient `.check(image)` method for performing
    image regression on PIL images.
    """
    return PILImageRegression(image_regression)


@pytest.fixture
def optical_pil_image() -> Image.Image:
    """Optical image loaded with PIL."""
    # Construct the path to your data file
    data_file = Path(__file__).parent / "data" / "optical_image.png"
    return Image.open(data_file)


@pytest.fixture
def s2_image() -> ee.Image:
    """A Sentinel 2 image that contains clouds, shadows, water and snow.

    This image is located in Argentina and Chile (Patagonia).
    """
    return ee.Image("COPERNICUS/S2_SR_HARMONIZED/20230120T142709_20230120T143451_T18GYT")


@pytest.fixture
def s2_collection_geometry() -> ee.Geometry:
    """A geometry for the S2 Collection."""
    return ee.Geometry.Polygon(
        [
            [
                [-63.1207279551548, -27.514421899185486],
                [-63.1207279551548, -27.604210067517904],
                [-63.00331157331886, -27.604210067517904],
                [-63.00331157331886, -27.514421899185486],
            ]
        ]
    )


@pytest.fixture
def s2_field() -> ee.Geometry:
    """A field to overlay in a S2 image."""
    return ee.Geometry.Polygon(
        [
            [
                [-63.06716960554542, -27.566557801770216],
                [-63.06373637800636, -27.551415512075334],
                [-63.08948558454933, -27.544338248641512],
                [-63.09497874861183, -27.561840327455865],
            ]
        ]
    )


@pytest.fixture
def s2_collection(s2_collection_geometry) -> ee.ImageCollection:
    """A Sentinel-2 image collection."""
    col = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(s2_collection_geometry)
        .filter(ee.Filter.lte("CLOUD_COVERAGE_ASSESSMENT", 10))
        .filterDate("2022-01-01", "2022-03-01")
    )
    return col


@pytest.fixture
def s2_image_overlay() -> ee.Geometry:
    """A Geometry Overlay."""
    return ee.Geometry.Polygon(
        [
            [
                [-71.73258, -42.81121],
                [-71.73258, -42.90131],
                [-71.58392, -42.90131],
                [-71.58392, -42.81121],
            ]
        ]
    )


@pytest.fixture
def s2_image_overlay_styled() -> ee.FeatureCollection:
    """Sentinel 2 image overlay styled."""
    return ee.FeatureCollection(
        [
            ee.Feature(
                ee.Geometry.Polygon(
                    [
                        [
                            [-63.09246352191069, -27.543873828758713],
                            [-63.09684088702299, -27.561452071810354],
                            [-63.06740096087553, -27.566626083437992],
                            [-63.06396773333647, -27.551255511600775],
                        ]
                    ]
                ),
                {
                    "system:index": "0",
                    "style": {"color": "blue", "fillColor": "#00000000", "width": 3},
                },
            ),
            ee.Feature(
                ee.Geometry.Polygon(
                    [
                        [
                            [-63.09031775469877, -27.558484513919126],
                            [-63.09083273882963, -27.561452071810354],
                            [-63.067272214842816, -27.56571304028485],
                            [-63.066585569335004, -27.56263146356792],
                        ]
                    ]
                ),
                {
                    "system:index": "1",
                    "style": {"color": "red", "fillColor": "#00000000", "width": 3},
                },
            ),
        ]
    )


@pytest.fixture
def s2_image_viz() -> dict:
    """Sentinel 2 image visualization parameters."""
    return {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
