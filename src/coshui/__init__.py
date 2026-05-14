from .state import CoshUI

from .core import CoshUIRenderer

Renderer = CoshUIRenderer # so that if users just do "import coshui", it'll look like 'with coshui.Renderer(coshui.PygameBackend(screen)):'.

from .widgets import Container, Grid, Modal, Button, Label, InputField, Checkbox, Image, Slider

from .utility import Ref, set_default_font, add_class, add_font, get_signal, create_theme, set_theme

from .types import CoshAlign, CoshJustify, CoshDirection, CoshSizing, CoshTextJustify, CoshTextAlign, CoshTextOverflow, CoshStyling, CoshOverflow, CoshPositioning, CoshMouseFilter, CoshMouseButton

ALIGN_START = CoshAlign.START
ALIGN_CENTER = CoshAlign.CENTER
ALIGN_END = CoshAlign.END
ALIGN_STRETCH = CoshAlign.STRETCH 

JUSTIFY_START = CoshJustify.START
JUSTIFY_CENTER = CoshJustify.CENTER
JUSTIFY_END = CoshJustify.END
JUSTIFY_SPACE_BETWEEN = CoshJustify.SPACE_BETWEEN
JUSTIFY_SPACE_AROUND = CoshJustify.SPACE_AROUND
JUSTIFY_SPACE_EVENLY = CoshJustify.SPACE_EVENLY

TEXT_HIDDEN = CoshTextOverflow.HIDDEN

HIDDEN = CoshOverflow.HIDDEN

LEFT = CoshMouseButton.LEFT
RIGHT = CoshMouseButton.RIGHT

IGNORE = CoshMouseFilter.IGNORE
STOP = CoshMouseFilter.STOP
PASS = CoshMouseFilter.PASS

RELATIVE = CoshPositioning.RELATIVE
ABSOLUTE = CoshPositioning.ABSOLUTE

FILL = CoshSizing.FILL
AUTO = CoshSizing.AUTO

from .themes import CoshTheme

from .animation import animate

from .backends.pygame_backend import PygameBackend


__all__ = ["CoshUI", "LEFT", "RIGHT", "CoshMouseFilter", "CoshPositioning", "CoshTextOverflow", "CoshOverflow", "get_signal", "create_theme", "set_theme", "add_font", "add_class", "CoshTextAlign", "CoshTextJustify", "CoshAlign", "CoshJustify", "CoshDirection", "FILL", "AUTO", "CoshStyling", "Container", "Grid", "Modal", "PygameBackend", "CoshUIRenderer", "CoshTheme", "animate", "Ref", "Button", "Image", "Label", "InputField", "Checkbox", "Slider", "set_default_font"]