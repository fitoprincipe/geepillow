"""Test eeimage module."""

from io import BytesIO

from geepillow.image import from_eeimage


class TestImage:
    def test_from_eeimage(self, s2_image, s2_image_overlay, image_regression):
        """Test eeimage module."""
        viz_params = {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
        image = from_eeimage(
            s2_image, dimensions=(500, 500), viz_params=viz_params, region=s2_image_overlay
        )

        # Convert the PIL image to bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # Save as PNG to BytesIO
        buffer.seek(0)  # Rewind the buffer to the beginning

        # Pass the bytes to pytest-image-regression
        image_regression.check(buffer.read())

    def test_from_eeimage_scale(self, s2_image, s2_image_overlay, image_regression):
        """Test eeimage module using a different scale."""
        viz_params = {"bands": ["B8", "B11", "B4"], "min": 0, "max": 4500}
        image = from_eeimage(
            s2_image,
            dimensions=(500, 500),
            viz_params=viz_params,
            scale=100,
            region=s2_image_overlay,
        )

        # Convert the PIL image to bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # Save as PNG to BytesIO
        buffer.seek(0)  # Rewind the buffer to the beginning

        # Pass the bytes to pytest-image-regression
        image_regression.check(buffer.read())

    def test_from_eeimage_overlay(self, s2_image, s2_image_overlay, image_regression):
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

        # Convert the PIL image to bytes
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # Save as PNG to BytesIO
        buffer.seek(0)  # Rewind the buffer to the beginning

        # Pass the bytes to pytest-image-regression
        image_regression.check(buffer.read())
