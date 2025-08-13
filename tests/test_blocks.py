"""Test blocks module."""

from geepillow import blocks


class TestBlock:
    """Test the basic base class Block."""

    def test_simple(self, pil_image_regression):
        """Test a simple block."""
        block = blocks.Block(background_color="blue", background_opacity=1)
        assert block.size == (500, 500)
        assert block.width == 500
        assert block.height == 500
        assert block.background_hex == "#0000FFFF"
        pil_image_regression.check(block.image)

    def test_resize(self, pil_image_regression):
        """Test resizing a simple block."""
        block = blocks.Block(background_color="red", background_opacity=1)
        block.size = (100, 100)
        assert block.size == (100, 100)
        assert block.width == 100
        assert block.height == 100
        assert block.background_hex == "#FF0000FF"
        pil_image_regression.check(block.image)
