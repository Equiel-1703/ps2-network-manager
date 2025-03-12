class GUIColors:
    """Color class for the GUI. We are using a deep purple theme."""

    DEEP_PURPLE = "#1A1326"
    DARK_LAVENDER = "#513E73"
    DEEP_MARINE = "#1F274B"
    LIGHT_GOLD = "#EBE350"
    LIGHT_GREEN = "#3BAD18"
    SOFT_RED = "#ED2427"
    
    OFF_WHITE = "#EDE7F6"
    WHITE = "#FFFFFF"

    BLACK = "#000000"
    OFF_BLACK = "#1C1C1C"

    @staticmethod
    def enlight_color(color: str, factor: float) -> str:
        """Enlights a color by a factor."""

        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = min(255, int(r + 255 * factor))
        g = min(255, int(g + 255 * factor))
        b = min(255, int(b + 255 * factor))

        return f"#{r:02X}{g:02X}{b:02X}"