"""Test blocks module."""

from geepillow import blocks


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
