"""Module to handle colors."""

import colorsys


class Color:
    """Base class for color."""

    def __init__(self, red: int, green: int, blue: int):
        """Color class to handle colors."""
        if red < 0 or red > 255:
            raise ValueError(f"'red' value must be between 0 and 255, found {red}")
        if green < 0 or green > 255:
            raise ValueError(f"'green' value must be between 0 and 255, found {green}")
        if blue < 0 or blue > 255:
            raise ValueError(f"'blue' value must be between 0 and 255, found {blue}")
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        """String representation of the color."""
        return f"Color({self.red}, {self.green}, {self.blue})"

    @classmethod
    def from_hex(cls, hex_color: str):
        """Create a color instance from hex."""
        hex_color = hex_color.lstrip("#")
        hex_color = hex_color[0:6]
        lv = len(hex_color)

        def convert(i):
            return int(hex_color[i : i + lv // 3], 16)

        return cls(*tuple(convert(i) for i in range(0, lv, lv // 3)))

    @classmethod
    def from_hsv(cls, hue: float, saturation: float, value: float):
        """Create a color instance from HSV values."""
        r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation, value)
        return cls(*tuple(int(c * 255) for c in (r, g, b)))

    def hex(self, opacity: float = 1.0) -> str:
        """Hex string of the color."""
        if opacity > 1 or opacity < 0:
            raise ValueError(f"Opacity must be between 0 and 1, found {opacity}")
        # Convert alpha to hexadecimal
        alpha_hex = f"{int(opacity * 255):02X}"
        hex_color = f"#{self.red:02X}{self.green:02X}{self.blue:02X}{alpha_hex}"
        return hex_color

    def rgb(self) -> tuple:
        """RGB of the color."""
        return self.red, self.green, self.blue

    def hsv(self) -> tuple:
        """Compute Hue Saturation and Value (HSV space)."""
        h, s, v = colorsys.rgb_to_hsv(self.red / 255, self.green / 255, self.blue / 255)
        return h, s, v


COMMON = dict(
    red=Color(255, 0, 0),
    green=Color(0, 255, 0),
    blue=Color(0, 0, 255),
    yellow=Color(255, 255, 0),
    cyan=Color(0, 255, 255),
    magenta=Color(255, 0, 255),
    orange=Color(255, 165, 0),
    white=Color(255, 255, 255),
    black=Color(0, 0, 0),
)


def color_from_string(string: str) -> Color:
    """Create a Color from a string.

    Accepts some common name like 'red' and if not in the common list, it will
    treat it as an hex color string.
    """
    if string.lower() in COMMON.keys():
        return COMMON[string.lower()]
    else:
        return Color.from_hex(string.lower())


def create(color: str | list | Color) -> Color:
    """Color dispatcher.

    Create a color according to the type of the object passed.

    Args:
        color: can be a string, a list (R,G,B) or a Color instance
    """
    if isinstance(color, str):
        return color_from_string(color)
    if isinstance(color, list):
        return Color(*color)
    if isinstance(color, Color):
        return color
    raise ValueError(f"Color '{color}' not recognized")
