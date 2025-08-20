"""Test grids module."""

from geepillow import blocks, grids


class TestGrid:
    """Test the Grid class."""

    def test_grid_simple(self, optical_pil_image, pil_image_regression):
        """Test a simple grid."""
        # create an image block
        im_block = blocks.ImageBlock(optical_pil_image)
        # create a text block
        txt_block_1 = blocks.TextBlock(text="Text block N°1", background_color="red")
        txt_block_2 = blocks.TextBlock(text="Text block N°2", background_color="green")
        txt_block_3 = blocks.TextBlock(text="Text block N°3", background_color="yellow")
        txt_block_4 = blocks.TextBlock(text="Text block N°4", background_color="blue")
        # create a grid
        grid = grids.Grid(
            blocks=[
                [im_block, txt_block_1, im_block, txt_block_2],
                [im_block, txt_block_3, im_block, txt_block_4],
            ],
            background_color="white",
        )
        pil_image_regression.check(grid.image)

    def test_grid_different_sizes(self, optical_pil_image, pil_image_regression):
        """Test a grid with different size blocks."""
        # create an image block
        im_block_1 = blocks.ImageBlock(optical_pil_image, background_color="yellow")
        im_block_2 = blocks.ImageBlock(optical_pil_image, background_color="blue", size=(200, 200))
        im_block_3 = blocks.ImageBlock(
            optical_pil_image, background_color="orange", size=(350, 650)
        )
        im_block_4 = blocks.ImageBlock(
            optical_pil_image, background_color="magenta", size=(650, 350)
        )
        txt_block_1 = blocks.TextBlock(
            text="Text block N1", size=(300, 300), background_color="red"
        )
        txt_block_2 = blocks.TextBlock(
            text="Text block N2", size=(400, 400), background_color="green"
        )
        txt_block_3 = blocks.TextBlock(
            text="Text block N3", size=(350, 650), background_color="yellow"
        )
        txt_block_4 = blocks.TextBlock(
            text="Text block N4", size=(400, 300), background_color="blue"
        )
        # create a grid
        grid = grids.Grid(
            blocks=[
                [im_block_1, im_block_2],
                [txt_block_1, txt_block_2],
                [im_block_3, im_block_4],
                [txt_block_3, txt_block_4],
            ]
        )
        pil_image_regression.check(grid.image)
