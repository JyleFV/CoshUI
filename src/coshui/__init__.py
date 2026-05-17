from .core import CoshUIRenderer

from .widgets import Container, Grid, Modal, Button, Label, InputField, Checkbox, Image, Slider

from .utility import Ref, set_default_font, add_class, add_font, get_signal, create_theme, set_theme

from .types import CoshAlign, CoshJustify, CoshDirection, CoshSizing, CoshTextJustify, CoshTextAlign, CoshTextOverflow, CoshStyling, CoshOverflow, CoshPositioning, CoshMouseFilter, CoshMouseButton, CoshSignals

# Align
ALIGN_START = CoshAlign.START
ALIGN_CENTER = CoshAlign.CENTER
ALIGN_END = CoshAlign.END
ALIGN_STRETCH = CoshAlign.STRETCH 

# Justify
JUSTIFY_START = CoshJustify.START
JUSTIFY_CENTER = CoshJustify.CENTER
JUSTIFY_END = CoshJustify.END
JUSTIFY_SPACE_BETWEEN = CoshJustify.SPACE_BETWEEN
JUSTIFY_SPACE_AROUND = CoshJustify.SPACE_AROUND
JUSTIFY_SPACE_EVENLY = CoshJustify.SPACE_EVENLY

# Text Overflow
TEXT_VISIBLE = CoshTextOverflow.VISIBLE
TEXT_HIDDEN = CoshTextOverflow.HIDDEN

# Text Align
TEXT_ALIGN_TOP = CoshTextAlign.TOP
TEXT_ALIGN_CENTER = CoshTextAlign.CENTER
TEXT_ALIGN_BOTTOM = CoshTextAlign.BOTTOM

# Text Justify
TEXT_JUSTIFY_LEFT = CoshTextJustify.LEFT
TEXT_JUSTIFY_CENTER = CoshTextJustify.CENTER
TEXT_JUSTIFY_RIGHT = CoshTextJustify.RIGHT

# Overflow
VISIBLE = CoshOverflow.VISIBLE
HIDDEN = CoshOverflow.HIDDEN

# Mouse Buttons - Currently doesn't do anything :/
MOUSE_LEFT = CoshMouseButton.LEFT
MOUSE_RIGHT = CoshMouseButton.RIGHT

# Mouse Filters
IGNORE = CoshMouseFilter.IGNORE
STOP = CoshMouseFilter.STOP
PASS = CoshMouseFilter.PASS

# Events
CLICKED = CoshSignals.CLICKED
RELEASED = CoshSignals.RELEASED
PRESSED = CoshSignals.PRESSED
HOVERED = CoshSignals.HOVERED
HOVER_ENTER = CoshSignals.HOVER_ENTER
HOVER_EXIT = CoshSignals.HOVER_EXIT

# Container Direction
ROW = CoshDirection.ROW
COLUMN = CoshDirection.COLUMN

# Positioning
RELATIVE = CoshPositioning.RELATIVE
ABSOLUTE = CoshPositioning.ABSOLUTE

# Sizing
FILL = CoshSizing.FILL
AUTO = CoshSizing.AUTO

from .themes import CoshTheme

from .animation import animate

from .backends.pygame_backend import PygameBackend
from .backends.raylib_backend import RaylibBackend

# TODO: Add the different flat variables
__all__ = [
    "CLICKED", 
    "RELEASED", 
    "PRESSED", 
    "HOVERED", 
    "HOVER_ENTER", 
    "HOVER_EXIT", 
    "LEFT", 
    "RIGHT", 
    "CoshMouseFilter", 
    "CoshPositioning", 
    "CoshTextOverflow", 
    "CoshOverflow", 
    "get_signal", 
    "create_theme", 
    "set_theme",
    "add_font", 
    "add_class", 
    "CoshTextAlign", 
    "CoshTextJustify", 
    "CoshAlign", 
    "CoshJustify", 
    "CoshDirection", 
    "FILL", 
    "AUTO", 
    "CoshStyling", 
    "Container", 
    "Grid", 
    "Modal", 
    "PygameBackend", 
    "RaylibBackend", 
    "CoshUIRenderer", 
    "CoshTheme", 
    "animate", 
    "Ref", 
    "Button", 
    "Image", 
    "Label", 
    "InputField", 
    "Checkbox", 
    "Slider", 
    "set_default_font"
]