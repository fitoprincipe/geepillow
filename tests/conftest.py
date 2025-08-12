"""Pytest session configuration."""

import ee
import pytest
import pytest_gee


def pytest_configure() -> None:
    """Initialize earth engine according to the environment."""
    pytest_gee.init_ee_from_service_account()


@pytest.fixture
def s2_image() -> ee.Image:
    """A Sentinel 2 image that contains clouds, shadows, water and snow.

    This image is located in Argentina and Chile (Patagonia).
    """
    return ee.Image("COPERNICUS/S2_SR_HARMONIZED/20230120T142709_20230120T143451_T18GYT")


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
