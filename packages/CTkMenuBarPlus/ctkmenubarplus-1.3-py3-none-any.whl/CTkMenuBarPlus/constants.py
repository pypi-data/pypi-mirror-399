from typing import Union, Tuple
import customtkinter

# Timing constants (in milliseconds)
DEFAULT_SUBMENU_DELAY = 500  # Delay before showing submenu on hover

# Layout and spacing constants
DEFAULT_PADDING = 3  # Internal padding for menu items
DEFAULT_CORNER_RADIUS_FACTOR = 5  # Factor for calculating corner radius scaling
DEFAULT_BORDER_WIDTH = 1  # Default border width for menu items
DEFAULT_WIDTH = 150  # Default menu width in pixels
DEFAULT_HEIGHT = 25  # Default menu item height in pixels
DEFAULT_CORNER_RADIUS = 10  # Default corner radius for rounded corners

# Theme color constants (light mode, dark mode)
DEFAULT_SEPARATOR_COLOR = ("grey80", "grey20")  # Separator line colors
DEFAULT_TEXT_COLOR = ("black", "white")  # Menu text colors
DEFAULT_HOVER_COLOR = ("grey75", "grey25")  # Hover colors
DEFAULT_BORDER_COLOR = "grey50"  # Border color
DEFAULT_FG_COLOR = "transparent"  # Foreground color

# Text constants
DEFAULT_FONT = ("helvetica", 12)

# Scrollbar constants
DEFAULT_MAX_VISIBLE_OPTIONS = 10  # Maximum options before scrollbar appears
SCROLLBAR_EXTRA_SPACE = 20  # Extra space for scrollbar
SCROLLBAR_WIDTH = 16  # Default scrollbar width

# Positioning constants
SUBMENU_HORIZONTAL_OFFSET = 1  # Additional horizontal offset for submenu positioning
SUBMENU_OVERLAP_PREVENTION = 1  # Minimal gap to prevent visual overlap

# Icon constants
DEFAULT_ICON_SIZE = 16  # Default icon size in pixels

# Type aliases for better readability
ColorType = Union[str, Tuple[str, str]]
WidgetType = Union[customtkinter.CTkBaseClass, '_CDMSubmenuButton']
RootType = Union[customtkinter.CTk, customtkinter.CTkToplevel]

__all__ = ["DEFAULT_SUBMENU_DELAY", "DEFAULT_PADDING", "DEFAULT_CORNER_RADIUS_FACTOR", "DEFAULT_BORDER_WIDTH",
           "DEFAULT_WIDTH", "DEFAULT_HEIGHT",  "DEFAULT_CORNER_RADIUS", "DEFAULT_SEPARATOR_COLOR",
           "DEFAULT_TEXT_COLOR", "DEFAULT_HOVER_COLOR", "DEFAULT_BORDER_COLOR", "DEFAULT_MAX_VISIBLE_OPTIONS",
           "SCROLLBAR_EXTRA_SPACE", "SCROLLBAR_WIDTH", "SUBMENU_HORIZONTAL_OFFSET", "SUBMENU_OVERLAP_PREVENTION",
           "DEFAULT_ICON_SIZE", "ColorType", "WidgetType", "RootType", "DEFAULT_FG_COLOR", "DEFAULT_FONT"]
