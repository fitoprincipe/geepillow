"""Test eeimage module."""

from geepillow.image import from_eeimage


class TestImage:
    def test_from_eeimage(self, s2_image, s2_image_overlay, pil_image_regression):
        """Test eeimage module."""
        viz_params = {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
        image = from_eeimage(
            s2_image, dimensions=(500, 500), viz_params=viz_params, region=s2_image_overlay
        )

        # Pass the bytes to pytest-image-regression
        pil_image_regression.check(image)

    def test_from_eeimage_scale(self, s2_image, s2_image_overlay, pil_image_regression):
        """Test eeimage module using a different scale."""
        viz_params = {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
        image = from_eeimage(
            s2_image,
            dimensions=(500, 500),
            viz_params=viz_params,
            scale=100,
            region=s2_image_overlay,
        )

        pil_image_regression.check(image)

    def test_from_eeimage_overlay(self, s2_image, s2_image_overlay, pil_image_regression):
        """Test eeimage module using an overlay fc."""
        viz_params = {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
        image = from_eeimage(
            s2_image,
            dimensions=(500, 500),
            viz_params=viz_params,
            region=s2_image_overlay,
            overlay=s2_image_overlay.buffer(-1000),
            overlay_style={"color": "red", "fillColor": "#00000000"},
        )

        pil_image_regression.check(image)

    def test_from_eeimage_overlay_styled(
        self, s2_collection, s2_image_overlay_styled, pil_image_regression
    ):
        """Test eeimage module using an overlay fc with per-feature styling."""
        viz_params = {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
        s2_i = s2_collection.filterDate("2022-02-26", "2022-02-27").first()
        image = from_eeimage(
            s2_i,
            dimensions=(500, 500),
            viz_params=viz_params,
            region=s2_image_overlay_styled.geometry().bounds().buffer(1000),
            overlay=s2_image_overlay_styled,
            style_property="style",
        )

        pil_image_regression.check(image)
