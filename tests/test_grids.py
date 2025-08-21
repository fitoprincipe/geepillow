"""Test grids module."""

from geepillow import blocks, eeblocks, grids


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

    def test_grid_not_square(self, optical_pil_image, pil_image_regression):
        """Test a grid with a number of blocks that do not fit the whole grid."""
        # create an image block
        im_block = blocks.ImageBlock(optical_pil_image, background_color="yellow")
        grid = grids.Grid(
            blocks=[[im_block, im_block, im_block], [im_block, im_block, im_block], [im_block]]
        )
        pil_image_regression.check(grid.image)


class TestEEImageCollectionBlock:
    """Test EEImageCollectionBlock."""

    def test_eeimagecollection_simple(
        self, s2_collection, s2_collection_geometry, s2_image_viz, pil_image_regression
    ):
        """Test EEImageCollectionBlock."""
        block = eeblocks.EEImageCollectionGrid(
            collection=s2_collection,
            n_columns=3,
            viz_params=s2_image_viz,
            scale=10,
            region=s2_collection_geometry,
        )
        pil_image_regression.check(block.image)

    def test_eeimagecollection_text(
        self, s2_collection, s2_collection_geometry, s2_image_viz, pil_image_regression
    ):
        """Test EEImageCollectionBlock with text."""
        text_pattern = (
            "S2 image from {system:time_start%tyyyy-MM-dd}\n"
            "with {CLOUD_COVERAGE_ASSESSMENT}% cloud coverage"
        )
        block = eeblocks.EEImageCollectionGrid(
            collection=s2_collection,
            n_columns=5,
            viz_params=s2_image_viz,
            scale=10,
            region=s2_collection_geometry,
            text_pattern=text_pattern,
            text_position="top",
        )
        pil_image_regression.check(block.image)

    def test_eeimagecollection_overlay(
        self, s2_collection, s2_field, s2_image_viz, pil_image_regression
    ):
        """Test EEImageCollectionBlock with overlay."""
        text_pattern = "Date: {system:time_start%tdd MMM yyyy}"
        block = eeblocks.EEImageCollectionGrid(
            collection=s2_collection,
            n_columns=4,
            text_pattern=text_pattern,
            text_position="bottom",
            viz_params=s2_image_viz,
            scale=10,
            region=s2_field.buffer(1000),
            overlay=s2_field,
            overlay_style={"color": "red", "fillColor": "#00000000"},
        )
        pil_image_regression.check(block.image)
