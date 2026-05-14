from __future__ import annotations
from typing import TypeVar, Generic, TYPE_CHECKING
import difflib
import os

from .cui_error import CoshUIError
from .state import CoshUI
from .types import *

if TYPE_CHECKING:
    from .themes import CoshTheme

T = TypeVar('T')
class Ref(Generic[T]):
    def __init__(self, value : T) -> None:
        self._value : T = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value : T):
        self._value = new_value

# ================ Fonts ================

def add_font(name : str, path : str):
    if not name or not path:
        raise CoshUIError("Please input a name or a path when adding fonts.")
    
    if not os.path.isfile(path):
        raise CoshUIError(f"Font path `{path}` does not exist or is not a file")
    
    CoshUI._font_library[name] = os.path.abspath(path)

def set_default_font(name : str):
    try:
        path = os.path.abspath(CoshUI._font_library[name])
        CoshUI._default_font = CoshUI._font_library.get(name)
    except KeyError:
        raise CoshUIError("That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments.") from None

# ================ Fonts ================

# ================ Signal Events ================

def get_signal(node_id : str, signal_name : str):
    # TODO: Add this robust check in the future:
    # signals = ["clicked", "released", "hover_enter", "hover_exit", "hovered", "pressed"]
    # if node_id not in CoshUI._signals:
    #     close_match = difflib.get_close_matches(node_id, CoshUI._signals, n=1)
    #     raise CoshUIError(f"`{node_id}` not found in signals registry. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    # if signal_name not in signals:
    #     close_match = difflib.get_close_matches(signal_name, signals, n=1)
    #     raise CoshUIError(f"`{signal_name}` is not a valid signal. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")

    return CoshUI._get_signal(node_id, signal_name)


# ================ Signal Events ================

# ================ Styling Classes ================

def add_class(name : str, style : CoshStyling):
    if not isinstance(style, CoshStyling):
        raise CoshUIError("Passed in style is not a CoshStyling object.")
    CoshUI._style_class[name] = style

# ================ Styling Classes ================

# ================ Preload Helpers ================

# NOTE: This currently does practically nothing due to how the architecture is made.
def preload_images(img_paths : str | list):
    """
    Preloads images to the backend to create image textures early.

    :param img_paths: Can be a string with a single value or a list of strings.
    :type img_paths: `str | list`
    :raises CoshUIError: If a path does not exist or is not a file

    .. note :: 
        `preload_images()` converts relative file paths to absolute paths based on the current working directory.

    .. warning::
        Preloading is not yet fully implemented. Images are currently loaded on first render.
        True preloading will be available in a future update.
    """

    if isinstance(img_paths, str):
        img_paths = [img_paths]
    
    for path in img_paths:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise CoshUIError(f"Image path `{abs_path}` doesn't exist or is not a file.")
        
        CoshUI._temp_paths.add(abs_path)

# ================ Preload Helpers ================

# ================ Themes ================

def create_theme(name : str, theme : CoshTheme):
    CoshUI._theme_registry[name] = theme

def set_theme(theme_name : str):
    theme = CoshUI._theme_registry.get(theme_name, None)
    if theme is None:
        close_match = difflib.get_close_matches(theme_name, CoshUI._theme_registry.keys(), n=1)
        raise CoshUIError(f"The theme `{theme_name}` does not exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    CoshUI._active_theme = theme

# ================ Themes ================

# ================ Helper Functions ================

def adjust_brightness_value(rgb, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)

def resolve_border_radius(value : int | float | tuple) -> tuple: 
    match value:
        case int() | float():
            return (value, value, value, value)
        case (a, b, c, d):
            return (a, b, c, d)
        case _:
            raise CoshUIError(f"Invalid border_radius `{value}`. Expected an int/float or a tuple of the 4 corner values (top-left, top-right, bottom-right, bottom-left).")

def point_in_rect(px, py, rx, ry, rw, rh):
    return (rx <= px <= rx + rw and ry <= py <= ry + rh)

def intersect_rect(r1, r2):
    x = max(r1[0], r2[0])
    y = max(r1[1], r2[1])
    w = min(r1[0] + r1[2], r2[0] + r2[2]) - x
    h = min(r1[1] + r1[3], r2[1] + r2[3]) - y
    if w <= 0 or h <= 0:
        return None
    return (x, y, w, h)

def merge_styles(base : CoshStyling, override : CoshStyling) -> CoshStyling:
    return CoshStyling(
        background_color=override.background_color if override.background_color is not None else base.background_color,
        alpha=override.alpha if override.alpha is not None else base.alpha,
        border=override.border if override.border is not None else base.border,
        border_radius=override.border_radius if override.border_radius is not None else base.border_radius,
        transform_position=override.transform_position if override.transform_position is not None else base.transform_position,
        transform_rotation=override.transform_rotation if override.transform_rotation is not None else base.transform_rotation,
        transform_scale=override.transform_scale if override.transform_scale is not None else base.transform_scale
    )