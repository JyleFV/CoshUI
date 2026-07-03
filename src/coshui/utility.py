from __future__ import annotations
from typing import TypeVar, Generic, TYPE_CHECKING, Callable, Optional
import difflib
import os
import math

from .cui_error import CoshUIError, warn
from .state import CoshUI
from .types import *

if TYPE_CHECKING:
    from .themes import CoshTheme

T = TypeVar('T')
class Ref(Generic[T]):
    def __init__(self, value : T) -> None:
        self._value : T = value
        self._on_change = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: T):
        old_value = self._value
        self._value = new_value
        if self._on_change and old_value != new_value:
            self._on_change(new_value)

    def on_change(self, callback: Callable):
        self._on_change = callback
        return self

# ================ Fonts ================

def add_font(name : str, base_path : str, bold : str = None, italic : str = None, bold_italic : str = None):
    if not name or not base_path:
        raise CoshUIError("Please input a name or a path when adding fonts.")

    variants = { "base_font" : base_path, "bold" : bold, "italic" : italic, "bold_italic" : bold_italic }

    for variant, path in variants.items():
        if path is not None and not os.path.isfile(path):
            raise CoshUIError(f"Font path `{path}` for `{variant}` of `{name}` does not exist or is not a file.")

    CoshUI._font_library[name] = { variant: (os.path.abspath(path) if path is not None else None) for variant, path in variants.items() }

def set_default_font(name: str):
    if name not in CoshUI._font_library:
        close_match = difflib.get_close_matches(name, CoshUI._font_library.keys(), n=1)
        raise CoshUIError(f"That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")

    CoshUI._default_font = name

# ================ Fonts ================

# ================ Signal Events ================

def get_signal(node_id : str, signal : CoshSignals):
    if node_id not in CoshUI._state_storage:
        close_match = difflib.get_close_matches(node_id, CoshUI._state_storage.keys(), n=1)
        raise CoshUIError(f"Unknown Node ID: `{node_id}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    return CoshUI._get_signal(node_id, signal)


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

# ================ Themes ================
# NOTE: user-facing function to create Particles
def create_particle():
    pass
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

def get_local_mouse(mouse_x, mouse_y, node_x, node_y, node_w, node_h, angle):
    center_x = node_x + (node_w / 2)
    center_y = node_y + (node_h / 2)
    
    rad = math.radians(angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    distance_x = mouse_x - center_x
    distance_y = mouse_y - center_y
    
    local_dx = distance_x * cos_a - distance_y * sin_a
    local_dy = distance_x * sin_a + distance_y * cos_a

    return (center_x + local_dx, center_y + local_dy)

def create_single_text_data(text : str, text_align : CoshTextAlign, text_justify : CoshTextJustify, text_overflow : CoshTextOverflow, text_color : tuple, font_size : int, font : str, strikethrough : bool, underline : bool):
    from .text_engine import TextRun
    text_data = TextData(text_align=text_align, text_justify=text_justify, text_overflow=text_overflow, default_color=text_color, default_font_size=font_size, default_font=font)
    text_data.text = text
    text_data.runs.append(TextRun(color=text_color, font_size=font_size, font=font, text=text, strikethrough=strikethrough, underline=underline))
    return text_data

def _rotate_point_around(px, py, cx, cy, angle_degrees):
    rad = math.radians(-angle_degrees)
    dx, dy = px - cx, py - cy
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return (cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a)

def _find_line_breaks(full_text, max_width, text_overflow, run_ranges):
    from ._defaults import ENGINE_DEFAULTS

    if text_overflow is not CoshTextOverflow.WRAP:
        return [(0, len(full_text))]  # one line, no wrapping

    def measure(text_slice, start_char):
        # find which run covers this char to get its font/size for measuring
        for run_start, run_end, run in run_ranges:
            if run_start <= start_char < run_end:
                size = run.font_size or ENGINE_DEFAULTS["font_size"]
                return CoshUI._measure_run(run.font, size, text_slice)[0]
        return 0

    lines = []
    line_start = 0
    current_line_end = 0
    i = 0
    while i <= len(full_text):
        next_space = full_text.find(' ', i)
        word_end = next_space if next_space != -1 else len(full_text)

        test_slice = full_text[line_start:word_end]
        test_width = measure(test_slice, line_start)

        if test_width <= max_width or current_line_end == line_start:
            current_line_end = word_end
            i = word_end + 1
        else:
            lines.append((line_start, current_line_end))
            line_start = current_line_end + 1
            i = line_start

        if next_space == -1:
            break

    lines.append((line_start, len(full_text)))
    return lines

def _justify_offset(node_width, line_width, justify):
    match justify:
        case CoshTextJustify.LEFT:   return 0.0
        case CoshTextJustify.CENTER: return (node_width - line_width) / 2
        case CoshTextJustify.RIGHT:  return node_width - line_width

def _align_offset(node_height, total_height, align):
    match align:
        case CoshTextAlign.TOP:    return 0.0
        case CoshTextAlign.CENTER: return (node_height - total_height) / 2
        case CoshTextAlign.BOTTOM: return node_height - total_height

def print_tree(node):
    print(f"Node: {node.__class__.__name__} with node_id: {node.id}\n")
    for child in node.children:
        print_tree(child)

def resolve_font_variant(font_entry, bold=False, italic=False, font_name=None):
    if font_entry is None:
        if font_name is not None:
            warn(f"Requested font `{font_name}` but it doesn't seem to be an existing font. Falling back to the default.")

        if bold and italic:
            return CoshUI._font_library[CoshUI._default_font].get("bold_italic")
        elif bold:
            return CoshUI._font_library[CoshUI._default_font].get("bold")
        elif italic:
            return CoshUI._font_library[CoshUI._default_font].get("italic")
        return CoshUI._font_library[CoshUI._default_font].get("base_font")

    variant_key = "bold_italic" if (bold and italic) else "bold" if bold else "italic" if italic else None
    if variant_key is None:
        return font_entry["base_font"]

    variant = font_entry.get(variant_key)
    if variant is None:
        warn(f"Requested `{variant_key}` variant for font `{font_name}` but it wasn't added with `add_font()`. Falling back to `base_font`.")
        return font_entry["base_font"]
    return variant