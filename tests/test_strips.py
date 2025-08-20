"""Test strips module."""

from geepillow import blocks, strips


class TestStrip:
    """Test the Strip class."""

    def test_strip_simple(self, optical_pil_image, pil_image_regression):
        """Test a simple strip."""
        # create an image block
        im_block = blocks.ImageBlock(optical_pil_image)
        # create a text block
        txt_block = blocks.TextBlock(
            text="An optical image\ncoming from Sentinel 2", background_color="red"
        )
        # create a strip
        strip = strips.Strip(blocks=[im_block, txt_block], background_color="blue")
        pil_image_regression.check(strip.image)

    def test_strip_vertical(self, optical_pil_image, pil_image_regression):
        """Test a vertical strip."""
        # create an image block
        im_block = blocks.ImageBlock(optical_pil_image)
        # create a text block
        txt_block = blocks.TextBlock(
            text="An optical image\ncoming from Sentinel 2", background_color="red"
        )
        # create a strip
        strip = strips.Strip(
            blocks=[im_block, txt_block], background_color="blue", orientation="vertical"
        )
        pil_image_regression.check(strip.image)

    def test_strip_nested(self, optical_pil_image, pil_image_regression):
        """Test a nested vertical strip into a horizontal strip."""
        im_block = blocks.ImageBlock(optical_pil_image)
        # create a text block
        txt_block_1 = blocks.TextBlock(text="Text block N°1", background_color="red")
        # create a strip
        strip_v1 = strips.Strip(
            blocks=[im_block, txt_block_1], background_color="blue", orientation="vertical"
        )
        txt_block_2 = blocks.TextBlock(text="Text block N°2", background_color="green")
        # create a strip
        strip_v2 = strips.Strip(
            blocks=[im_block, txt_block_2], background_color="blue", orientation="vertical"
        )
        strip_h = strips.Strip(
            blocks=[strip_v1, strip_v2], background_color="white", orientation="horizontal"
        )
        pil_image_regression.check(strip_h.image)

    def test_strip_smaller(self, optical_pil_image, pil_image_regression):
        """Test a smaller strip."""
        im_block = blocks.ImageBlock(optical_pil_image)  # 500x500
        # create a text block
        txt_block = blocks.TextBlock(
            text="An optical image\ncoming from Sentinel 2", background_color="red"
        )  # 132x40
        # create a strip
        strip = strips.Strip(blocks=[im_block, txt_block], size=(400, 300), background_color="blue")
        pil_image_regression.check(strip.image)
