from __future__ import annotations
from typing import TypeVar, Generic, TYPE_CHECKING, Callable, Optional
import difflib
import os

from .animation import PROPERTY_MAP, PROPERTY_TYPE_MAP, EASING_MAP, Tween, ease_linear
from .cui_error import CoshUIError, warn
from .state import CoshUI
from .types import *

if TYPE_CHECKING:
    from .themes import CoshTheme
    from .text_engine import TextStyle

T = TypeVar('T')
class Ref(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value
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

def add_font(name: str, base_path: str, bold: str = None, italic: str = None, bold_italic: str = None):
    if not name or not base_path:
        raise CoshUIError("Please input a name or a path when adding fonts.")

    variants = { "base_font": base_path, "bold": bold, "italic": italic, "bold_italic": bold_italic }

    for variant, path in variants.items():
        if path is not None and not os.path.isfile(path):
            raise CoshUIError(f"Font path `{path}` for `{variant}` of `{name}` does not exist or is not a file.")

    CoshUI._font_library[name] = { variant: (os.path.abspath(path) if path is not None else None) for variant, path in variants.items() }

def set_default_font(name: str):
    if name not in CoshUI._font_library:
        close_match = difflib.get_close_matches(name, CoshUI._font_library.keys(), n=1)
        raise CoshUIError(f"That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")

    CoshUI._default_font = name

def get_signal(node_id: str, signal: CoshSignals):
    if node_id not in CoshUI._state_storage:
        close_match = difflib.get_close_matches(node_id, CoshUI._state_storage.keys(), n=1)
        raise CoshUIError(f"Unknown Node ID: `{node_id}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    return CoshUI._get_signal(node_id, signal)

def add_class(name: str, style: CoshStyling | TextStyle):
    from .text_engine import TextStyle, KEYWORD_MAP, TAGS
    if isinstance(style, CoshStyling):
        if name in CoshUI._style_class:
            raise CoshUIError(f"The class name `{name}` already exists. Did you make duplicate classes?")
        CoshUI._style_class[name] = style
    elif isinstance(style, TextStyle):
        if name in (KEYWORD_MAP.keys() | TAGS.keys()):
            raise CoshUIError(f"The tag `{name}` already exists and cannot be used as a class name. Please choose a different one.")
        if name in CoshUI._text_style_class:
            raise CoshUIError(f"The text class name `{name}` already exists. Did you make duplicate classes?")
        CoshUI._text_style_class[name] = style
    else:
        raise CoshUIError("Passed in style is not a CoshStyling or TextStyle object.")

# NOTE: This currently does practically nothing due to how the architecture is made.
def preload_images(img_paths: str | list):
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

def create_theme(name: str, theme: CoshTheme):
    CoshUI._theme_registry[name] = theme

def set_theme(theme_name: str):
    theme = CoshUI._theme_registry.get(theme_name, None)
    if theme is None:
        close_match = difflib.get_close_matches(theme_name, CoshUI._theme_registry.keys(), n=1)
        raise CoshUIError(f"The theme `{theme_name}` does not exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    CoshUI._active_theme = theme

def animate(n_property: str, target_id: str, end_value, duration: float, easing: str) -> Tween:
    """
    Animates a node property over time. 
    
    This function calls the TweenManager to create a `Tween` object. The TweenManager deals
    with Tween lifetime, storage, and updates.

    Parameters
    - n_property: The property you want to animate (e.g., 'transform_position', 'transform_scale', or 'alpha').
    - target_id: The id of the node instance the animation is applied to.
    - end_value: The final target value to reach by the end of the animation.
    - duration: Animation length in seconds.
    - easing: The easing curve name. Defaults to 'linear' if not passed.

    Returns
    - Tween: Returns the tween it's working on.
    """

    if n_property not in PROPERTY_MAP:
        close_match = difflib.get_close_matches(n_property, PROPERTY_MAP.keys(), n=1)
        raise CoshUIError(f"Unknown property `{n_property}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`? Valid properties are: {list(PROPERTY_MAP.keys())}.")
    
    if target_id not in CoshUI._state_storage:
        close_match = difflib.get_close_matches(target_id, CoshUI._state_storage.keys(), n=1)
        raise CoshUIError(f"ID `{target_id}` does not exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    if easing not in EASING_MAP:
        close_match = difflib.get_close_matches(easing, EASING_MAP.keys(), n=1)
        raise CoshUIError(f"Unknown easing curve: `{easing}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`? Valid properties are: {list(EASING_MAP.keys())}.")

    path, lerp_fn = PROPERTY_MAP[n_property]
    expected_type = PROPERTY_TYPE_MAP.get(lerp_fn)

    if expected_type and not isinstance(end_value, expected_type):
        raise CoshUIError(f"Property `{n_property}` expects `{expected_type}`, got `{type(end_value).__name__}`.")

    ease_fn = EASING_MAP.get(easing, ease_linear)
    return CoshUI._tween_manager.create_tween(n_property, target_id, end_value, duration, ease_fn, path, lerp_fn)

# NOTE: user-facing function to create Particles
def create_particle():
    pass