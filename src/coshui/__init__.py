from .core import CoshUIRenderer

from .widgets import Container, Grid, Modal, Button, Label, Checkbox, Image, Slider, Dropdown, RichLabel

from .text_engine import TextStyle

from .user_functions import Ref, set_default_font, add_class, add_font, get_signal, create_theme, set_theme, animate

from .types import CoshMode, CoshAlign, CoshJustify, CoshDirection, CoshSizing, CoshPercentage, CoshTextJustify, CoshTextAlign, CoshTextOverflow, CoshStyling, CoshOverflow, CoshPositioning, CoshMouseFilter, CoshMouseButton, CoshSignals

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
TEXT_WRAP = CoshTextOverflow.WRAP

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
PERCENTAGE = CoshPercentage

# Mode
NORMAL = CoshMode.NORMAL
DEBUG = CoshMode.DEBUG

from .themes import CoshTheme

def __getattr__(name):
    if name == "PygameBackend":
        from .backends.frameworks.pygame_backend import PygameBackend
        return PygameBackend
    if name == "RaylibBackend":
        from .backends.frameworks.raylib_backend import RaylibBackend
        return RaylibBackend
    if name == "ModernGLBackend":
        from .backends.graphics.gl_related.moderngl_backend import ModernGLBackend
        return ModernGLBackend
    if name == "PyOpenGLBackend":
        from .backends.graphics.gl_related.pyopengl_backend import PyOpenGLBackend
        return PyOpenGLBackend
    raise AttributeError(f"module 'coshui' has no attribute {name!r}")

from .backends.graphics.gl_related.gl_window_drivers import Windower

GLFW = Windower.GLFW
MGLW = Windower.MGLW

# TODO: Add the different flat variables
__all__ = [
    # Core
    "CoshUIRenderer",
    "animate",
    "Ref",

    # Widgets
    "Container",
    "Grid",
    "Modal",
    "Button",
    "Label",
    "Checkbox",
    "Image",
    "Slider",
    "Dropdown",
    "RichLabel",

    # Backends
    "PygameBackend",
    "RaylibBackend",
    "ModernGLBackend",
    "PyOpenGLBackend",

    # Themes
    "CoshTheme",
    "create_theme",
    "set_theme",

    # Utility
    "get_signal",
    "add_font",
    "add_class",
    "set_default_font",

    # Types (raw enums)
    "CoshStyling",
    "TextStyle"

    # Align
    "ALIGN_START",
    "ALIGN_CENTER",
    "ALIGN_END",
    "ALIGN_STRETCH",

    # Justify
    "JUSTIFY_START",
    "JUSTIFY_CENTER",
    "JUSTIFY_END",
    "JUSTIFY_SPACE_BETWEEN",
    "JUSTIFY_SPACE_AROUND",
    "JUSTIFY_SPACE_EVENLY",

    # Text Overflow
    "TEXT_VISIBLE",
    "TEXT_HIDDEN",
    "TEXT_WRAP",

    # Text Align
    "TEXT_ALIGN_TOP",
    "TEXT_ALIGN_CENTER",
    "TEXT_ALIGN_BOTTOM",

    # Text Justify
    "TEXT_JUSTIFY_LEFT",
    "TEXT_JUSTIFY_CENTER",
    "TEXT_JUSTIFY_RIGHT",

    # Overflow
    "VISIBLE",
    "HIDDEN",

    # Mouse Buttons
    "MOUSE_LEFT",
    "MOUSE_RIGHT",

    # Mouse Filters
    "IGNORE",
    "STOP",
    "PASS",

    # Signals
    "CLICKED",
    "RELEASED",
    "PRESSED",
    "HOVERED",
    "HOVER_ENTER",
    "HOVER_EXIT",

    # Direction
    "ROW",
    "COLUMN",

    # Positioning
    "RELATIVE",
    "ABSOLUTE",

    # Sizing
    "FILL",
    "AUTO",
    "PERCENTAGE",

    # Mode
    "NORMAL",
    "DEBUG",

    # GL Specific Windowers
    "GLFW",
    "MGLW"
]