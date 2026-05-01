from .cui_error import CoshUIError
from dataclasses import dataclass, field
from typing import NamedTuple
from enum import Enum

# ((0, 0)) ((5, 0))
# [(0, 5), (0, 0)]

@dataclass
class CoshLayout:
    true_position : tuple = (0, 0) 
    width : float = 0.0
    height : float = 0.0
    padding : float = 0.0
    margin : float = 0.0

@dataclass
class CoshStyling:
    background_color : tuple | None = None
    alpha : int | None = None
    # gradients : tuple[tuple[tuple[int, int, int], tuple[int, int, int]], str] | None = None
    border_radius : int | tuple = 0
    transform_position : tuple = (0, 0)
    transform_rotation : float = 0.0
    transform_scale : float = 1.0

    # Lets user use a 4 value tuple for background_color or a 3 value tuple with an explicit alpha field or default.
    def __post_init__(self):
        if self.background_color is not None and len(self.background_color) == 4:
            r, g, b, a = self.background_color
            self.background_color = (r, g, b)
            if self.alpha is None:
                self.alpha = a
        
        if self.alpha is None:
            self.alpha = 255

class CoshOverflow(Enum):
    HIDDEN = 0
    VISIBLE = 1
    SCROLL = 2

class CoshDirection(Enum):
    ROW = 0
    COLUMN = 1

class CoshAlignment(Enum):
    TOP = 0
    BOTTOM = 1
    CENTER = 2
    LEFT = 3
    RIGHT = 4

class CoshSizing(Enum):
    FIXED = 0
    FIT = 1
    FILL = 2

class RenderContext(NamedTuple):
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
    border_radius : tuple | None = None
    alpha : int = 0
    transform_scale : float = 1.0
    # Text
    text : str | None = None
    font : str | None = None
    # Image
    image_path : str | None = None

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

__all__ = ['CoshLayout', 'CoshStyling', 'CoshAlignment', 'CoshDirection', 'CoshSizing','lerp_float', 'lerp_tuple', 'ease_linear', 'ease_in', 'ease_out', 'ease_in_out']