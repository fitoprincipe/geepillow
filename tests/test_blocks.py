"""Test blocks module."""

from geepillow import blocks, eeblocks, fonts


class TestBlock:
    """Test the basic base class Block."""

    def test_simple(self, pil_image_regression):
        """Test a simple block."""
        block = blocks.Block(background_color="blue")
        assert block.size == (500, 500)
        assert block.width == 500
        assert block.height == 500
        assert block.background_hex == "#0000FFFF"
        pil_image_regression.check(block.image)

    def test_resize(self, pil_image_regression):
        """Test resizing a simple block."""
        block = blocks.Block(background_color="red")
        block.size = (100, 100)
        assert block.size == (100, 100)
        assert block.width == 100
        assert block.height == 100
        assert block.background_hex == "#FF0000FF"
        pil_image_regression.check(block.image)


class TestImageBlock:
    """Test the ImageBlock."""

    def test_simple_image_block(self, optical_pil_image, pil_image_regression):
        """Test a simple image block."""
        block = blocks.ImageBlock(optical_pil_image)
        pil_image_regression.check(block.image)

    def test_image_inside_bigger(self, optical_pil_image, pil_image_regression):
        """Test an image inside a bigger block."""
        block = blocks.ImageBlock(optical_pil_image, size=(800, 800), background_color="red")
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_fit_and_keep_proportion_same_proportion(
        self, optical_pil_image, pil_image_regression
    ):
        """Test an image inside a smaller block.

        The block has the same proportion as the image.
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(100, 100),
            background_color="red",
            keep_proportion=True,
            fit_block=True,
        )
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_fit_and_keep_proportion_different_proportion(
        self, optical_pil_image, pil_image_regression
    ):
        """Test an image inside a smaller block.

        The block has different proportion as the image.
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(300, 100),
            background_color="red",
            keep_proportion=True,
            fit_block=True,
        )
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_fit_and_keep_proportion_wider(
        self, optical_pil_image, pil_image_regression
    ):
        """Test an image inside a smaller block.

        The block is wider than the image but not higher.
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 100),
            background_color="red",
            keep_proportion=True,
            fit_block=True,
        )
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_fit_and_keep_proportion_higher(
        self, optical_pil_image, pil_image_regression
    ):
        """Test an image inside a smaller block.

        The block is higher than the image but not wider.
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(100, 800),
            background_color="red",
            keep_proportion=True,
            fit_block=True,
        )
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_fit_and_keep_proportion_higher_position(
        self, optical_pil_image, pil_image_regression
    ):
        """Test an image inside a smaller block.

        - position="top-left"
        - keep_proportion=True
        - fit_block=True
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(200, 600),
            position="top-left",
            background_color="red",
            keep_proportion=True,
            fit_block=True,
        )
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_deform(self, optical_pil_image, pil_image_regression):
        """Test an image inside a smaller block.

        - keep_proportion=False
        - fit_block=True
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(200, 600),
            background_color="red",
            keep_proportion=False,
            fit_block=True,
        )
        pil_image_regression.check(block.image)

    def test_image_inside_smaller_dont_fit(self, optical_pil_image, pil_image_regression):
        """Test an image inside a smaller block.

        position="top-left"
        keep_proportion=True
        fit_block=False
        """
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(200, 600),
            position="top-left",
            background_color="red",
            keep_proportion=True,
            fit_block=False,
        )
        pil_image_regression.check(block.image)

    def test_image_position_top_left(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with top-left position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="top-left",
        )
        pil_image_regression.check(block.image)

    def test_image_position_top_center(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with top-center position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="top-center",
        )
        pil_image_regression.check(block.image)

    def test_image_position_top_right(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with top-right position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            background_opacity=0.5,
            position="top-right",
        )
        pil_image_regression.check(block.image)

    def test_image_position_center_left(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with center-left position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="center-left",
        )
        pil_image_regression.check(block.image)

    def test_image_position_center_right(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with center-right position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="center-right",
        )
        pil_image_regression.check(block.image)

    def test_image_position_bottom_left(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with bottom-left position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="bottom-left",
        )
        pil_image_regression.check(block.image)

    def test_image_position_bottom_center(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with bottom-center position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="bottom-center",
        )
        pil_image_regression.check(block.image)

    def test_image_position_bottom_right(self, optical_pil_image, pil_image_regression):
        """Test ImageBlock with bottom-right position."""
        block = blocks.ImageBlock(
            optical_pil_image,
            size=(800, 800),
            background_color="blue",
            position="bottom-right",
        )
        pil_image_regression.check(block.image)


class TestTextBlock:
    """Test the TextBlock."""

    def test_text_simple(self, pil_image_regression):
        """Test a simple text block."""
        block = blocks.TextBlock("simple")
        pil_image_regression.check(block.image)

    def test_text_background_color(self, pil_image_regression):
        """Test a simple text block."""
        block = blocks.TextBlock("simple", background_color="red")
        pil_image_regression.check(block.image)

    def test_text_color(self, pil_image_regression):
        """Test a simple text block with colored text."""
        block = blocks.TextBlock("simple", size=(50, 50), text_color="red", background_color="blue")
        pil_image_regression.check(block.image)

    def test_text_font_size(self, pil_image_regression):
        """Test a simple text block with colored text."""
        font = fonts.opensans_regular(24)
        block = blocks.TextBlock(
            "simple",
            font=font,
            size=(100, 100),
            text_color="red",
            text_opacity=1,
            background_color="blue",
        )
        pil_image_regression.check(block.image)

    def tests_text_change_font(self, pil_image_regression):
        """Test a simple text block with colored text."""
        font = fonts.opensans_regular(24)
        # this block should look has "test_text_font_size" output
        block = blocks.TextBlock(
            "simple",
            font=font,
            size=(100, 100),
            text_color="red",
            text_opacity=1,
            background_color="blue",
        )
        # now we change the font
        block.font = fonts.opensans_bold(12)
        pil_image_regression.check(block.image)


class TestEEImageBlock:
    """Test EEImageBlock."""

    def test_eeimage_simple(self, s2_image, s2_image_overlay, s2_image_viz, pil_image_regression):
        """Test EEImageBlock."""
        block = eeblocks.EEImageBlock(s2_image, viz_params=s2_image_viz, region=s2_image_overlay)
        pil_image_regression.check(block.image)

    def test_eeimage_bigger_block(
        self, s2_image, s2_image_overlay, s2_image_viz, pil_image_regression
    ):
        """Test EEImageBlock with a bigger block than dimensions."""
        block = eeblocks.EEImageBlock(
            s2_image,
            viz_params=s2_image_viz,
            region=s2_image_overlay,
            dimensions=(500, 500),
            size=(1000, 1000),
            background_color="red",
            position="top-left",
        )
        pil_image_regression.check(block.image)
