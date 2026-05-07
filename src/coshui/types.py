from dataclasses import dataclass, field
from typing import NamedTuple
from enum import Enum

from .cui_error import CoshUIError

@dataclass
class CoshLayout:
    true_position : tuple = (0, 0) 
    width : float | None = None
    height : float | None = None
    padding : float = 0.0
    margin : float = 0.0

@dataclass
class CoshStyling:
    background_color : tuple | None = None
    alpha : int | None = None
    # gradients : tuple[tuple[tuple[int, int, int], tuple[int, int, int]], str] | None = None
    border : tuple | None = None
    border_radius : int | tuple | None = None
    transform_position : tuple | None = None
    transform_rotation : float | None = None
    transform_scale : float | None = None

    def __post_init__(self):
        # Lets user use a 4 value tuple for background_color or a 3 value tuple with an explicit alpha field or default.
        if self.background_color is not None and len(self.background_color) == 4:
            r, g, b, a = self.background_color
            self.background_color = (r, g, b)
            if self.alpha is None:
                self.alpha = a

        if self.border is not None:
            if is_valid_border(self.border):
                pass # correct format already
            elif isinstance(self.border, tuple) and len(self.border) == 4:
                try:    
                    r, g, b, width = self.border
                    self.border = ((r, g, b), width)
                except TypeError:
                    raise CoshUIError(f"Invalid `border` value `{self.border}`. Expected `((r, g, b), width)` or `(r, g, b, width)` e.g. `((255, 0, 0), 2)` or `(255, 0, 0, 2)`.") from None
            else:
                raise CoshUIError(f"Invalid `border` value `{self.border}`. Expected `((r, g, b), width)` or `(r, g, b, width)` e.g. `((255, 0, 0), 2)` or `(255, 0, 0, 2)`.")

class CoshOverflow(Enum):
    HIDDEN = 0
    VISIBLE = 1
    SCROLL = 2

class CoshTextOverflow(Enum):
    HIDDEN = 0  
    VISIBLE = 1
    WRAP = 2

class CoshPositioning(Enum):
    RELATIVE = 0
    ABSOLUTE = 1

class CoshDirection(Enum):
    ROW = 0
    COLUMN = 1

class CoshTextJustify(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class CoshTextAlign(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2

class CoshJustify(Enum):
    START = 0
    CENTER = 1
    END = 2
    SPACE_BETWEEN = 3
    SPACE_AROUND = 4
    SPACE_EVENLY = 5

class CoshAlign(Enum):
    START = 0
    CENTER = 1
    END = 2
    STRETCH = 3

class CoshSizing(Enum):
    FIXED = 0
    FIT = 1
    FILL = 2

class RenderContext(NamedTuple):
    # Node-specific
    id : str | None = None
    # Layout
    x : float = 0.0
    y : float = 0.0
    width : float = 0.0
    height : float = 0.0
    z_index : int = 0
    transform_x : float = 0.0
    transform_y : float = 0.0
    # Visual
    background_color : tuple | None = None
    border_radius : int | tuple = 0
    transform_scale : float = 1.0
    border : tuple | None = None
    alpha : int = 0
    # Interaction
    mouse_filter : bool = True
    # Text
    text : str | None = None
    text_color : tuple = (255, 255, 255)
    font : str | None = None
    font_size : int = 18
    text_justify : CoshTextJustify = CoshTextJustify.CENTER
    text_align : CoshTextAlign = CoshTextAlign.CENTER
    text_overflow : CoshTextOverflow = CoshTextOverflow.VISIBLE
    # Image
    image_src : str | None = None
    # Overflow-logic
    clip_rect : tuple | None = None

def lerp_float(start_value : float | int, end_value, time):
    return start_value + time * (end_value - start_value)

def lerp_tuple(start_tup, end_tup, time):
    return tuple(lerp_float(s, e, time) for s, e in zip(start_tup, end_tup))

def ease_linear(t : float):
    return t

def ease_in(t : float):
    return t * t

def ease_out(t : float):
    return 1 - (1 - t) * (1 - t)

def ease_in_out(t : float):
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2 

# HELPER
def is_valid_border(border):
    return (
        isinstance(border, tuple) and len(border) == 2 and
        isinstance(border[0], tuple) and len(border[0]) == 3 and
        all(isinstance(x, int) for x in border[0]) and
        isinstance(border[1], int)
    )

__all__ = ['CoshPositioning', 'CoshOverflow', 'CoshLayout', 'CoshStyling', 'CoshAlign', 'CoshJustify', 'CoshDirection', 'CoshSizing','lerp_float', 'lerp_tuple', 'ease_linear', 'ease_in', 'ease_out', 'ease_in_out']