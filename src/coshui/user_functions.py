from __future__ import annotations
from typing import TypeVar, Generic, TYPE_CHECKING, Callable
import difflib
import os

from .animation import PROPERTY_MAP, PROPERTY_TYPE_MAP, EASING_MAP, Tween, ease_linear
from .cui_error import CoshUIError
from .utility import merge_themes
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

def add_font(name: str, base_path: str, bold: str | None = None, italic: str | None = None, bold_italic: str | None = None):
    """
    Adds a new font that users can set text to.

    ### Parameters

    - **name**: The name of the new font.
    - **base_path**: A required field which is the base font path. This will act as the default when passing in the font name in the `font` field.
    - **bold**: The font path that will be used when the `bold` field is set to True on TextNodes or CoshML markup.
    - **italic**: The font path that will be used when the `italic` field is set to True on TextNodes or CoshML markup.
    - **bold_italic**: The font path that will be used when both the `bold` field and `italic` field are set to True on TextNodes or CoshML markup.
    """

    if not name or not base_path:
        raise CoshUIError.Main("Please input a name or a path when adding fonts.")

    variants = { "base_font": base_path, "bold": bold, "italic": italic, "bold_italic": bold_italic }

    for variant, path in variants.items():
        if path is not None and not os.path.isfile(path):
            raise CoshUIError.Main(f"Font path `{path}` for `{variant}` of `{name}` does not exist or is not a file.")

    CoshUI._font_library[name] = { variant: (os.path.abspath(path) if path is not None else None) for variant, path in variants.items() }

def set_default_font(name: str):
    """
    Sets the **default** font used by every text rendered in CoshUI.

    ### Parameters

    - **name**: The name of an existing font.

    If the user adds their own font, remember to put this ***after*** the `add_font()` declaration.
    """
    
    if name not in CoshUI._font_library:
        close_match = difflib.get_close_matches(name, CoshUI._font_library.keys(), n=1)
        raise CoshUIError.Main(f"That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")

    CoshUI._default_font = name

def get_signal(node_id: str, signal: CoshSignals):
    """
    Checks if a specific Node has been interacted with by checking the signal registry.

    ### Parameters

    - **node_id**: The id of the Node to specifically check.
    - **signal**: The interaction event to check, this can be `CLICKED`, `RELEASED`, `PRESSED`, `HOVERED`, `HOVER_ENTER`, and `HOVER_EXIT`.

    ### Returns

    - **Boolean**: Returns true or false depending on if that interaction event did happen to that Node. 
    """

    if node_id not in CoshUI._state_storage:
        close_match = difflib.get_close_matches(node_id, CoshUI._state_storage.keys(), n=1)
        raise CoshUIError.Main(f"Unknown Node ID: `{node_id}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    return CoshUI._get_signal(node_id, signal)

def add_class(name: str, style: CoshStyling | TextStyle):
    """
    Creates *style* classes that can be used as Node styles or CoshML styles depending on whether a `CoshStyling` object or `TextStyle` object was passed.

    ### Parameters

    - **name**: A name for the class that will be used when passing in to the `classes` field or straight in markup.
    - **style**: A `CoshStyling` or `TextStyle` object that dictates the style and whether it will be used for Nodes or CoshML markup.

    This helps with *reusability*. If users have a style that multiple Nodes or text use, creating a class and passing it in is much easier than copy and pasting.
    """

    from .text_engine import TextStyle, KEYWORD_MAP, TAGS
    if isinstance(style, CoshStyling):
        if name in CoshUI._style_class:
            raise CoshUIError.Main(f"The class name `{name}` already exists. Did you make duplicate classes?")
        CoshUI._style_class[name] = style
    elif isinstance(style, TextStyle):
        if name in (KEYWORD_MAP.keys() | TAGS.keys()):
            raise CoshUIError.Main(f"The tag `{name}` already exists and cannot be used as a class name. Please choose a different one.")
        if name in CoshUI._text_style_class:
            raise CoshUIError.Main(f"The text class name `{name}` already exists. Did you make duplicate classes?")
        CoshUI._text_style_class[name] = style
    else:
        raise CoshUIError.Main("Passed in style is not a CoshStyling or TextStyle object.")

def create_theme(name: str, theme: CoshTheme, inherit: str | None = None):
    """
    Creates a new theme to be put in the `_theme_registry` that is fully customized by the user.

    ### Parameters

    - **name**: A name to give the new theme that will be set in the `_theme_registry`.
    - **theme**: A `CoshTheme` object that holds all the node values and tokens to be set as defaults for Nodes.
    - **inherit**: Takes in the theme name of an existing theme that the new theme will inherit from (makes it so users don't have to fill in every value for every node and token).
    
    When inheriting from an existing theme, it will act as the **base** that your new theme overrides. If it does not have a value (meaning it's None), it will act as a completely new override.
    """

    final_theme = theme

    if inherit is not None:
        base_theme = CoshUI._theme_registry.get(inherit, None)
        if base_theme is None:
            close_match = difflib.get_close_matches(inherit, CoshUI._theme_registry.keys(), n=1)
            raise CoshUIError.Main(f"The theme `{inherit}` doesn't exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
        else:
            final_theme = merge_themes(base_theme, theme)

    CoshUI._theme_registry[name] = final_theme

def set_theme(theme_name: str):
    """
    Sets the default theme used throughout the library. If used on a user-made theme, call this function ***after*** the `create_theme()` declaration.

    ### Parameters

    - **theme_name**: A name of an existing theme.
    """

    theme = CoshUI._theme_registry.get(theme_name, None)
    if theme is None:
        close_match = difflib.get_close_matches(theme_name, CoshUI._theme_registry.keys(), n=1)
        raise CoshUIError.Main(f"The theme `{theme_name}` does not exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    CoshUI._active_theme = theme

def animate(n_property: str, target_id: str, end_value, duration: float, easing: str = "linear") -> Tween:
    """
    Animates a node property over time. This function calls the TweenManager to create a `Tween` object. The TweenManager deals with Tween lifetime, storage, and updates.

    ### Parameters
    
    - **n_property**: The property you want to animate (e.g., 'transform_position', 'transform_scale', or 'alpha').
    - **target_id**: The id of the node instance the animation is applied to.
    - **end_value**: The final target value to reach by the end of the animation.
    - **duration**: Animation length in seconds.
    - **easing**: The easing curve name. Defaults to 'linear' if not passed.

    ### Returns

    - **Tween**: Returns the tween that is managing the animation.
    """

    if n_property not in PROPERTY_MAP:
        close_match = difflib.get_close_matches(n_property, PROPERTY_MAP.keys(), n=1)
        raise CoshUIError.Main(f"Unknown property `{n_property}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`? Valid properties are: {list(PROPERTY_MAP.keys())}.")
    
    if target_id not in CoshUI._state_storage:
        close_match = difflib.get_close_matches(target_id, CoshUI._state_storage.keys(), n=1)
        raise CoshUIError.Main(f"ID `{target_id}` does not exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    if easing not in EASING_MAP:
        close_match = difflib.get_close_matches(easing, EASING_MAP.keys(), n=1)
        raise CoshUIError.Main(f"Unknown easing curve: `{easing}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`? Valid properties are: {list(EASING_MAP.keys())}.")

    path, lerp_fn = PROPERTY_MAP[n_property]
    expected_type = PROPERTY_TYPE_MAP.get(lerp_fn)

    if expected_type and not isinstance(end_value, expected_type):
        raise CoshUIError.Main(f"Property `{n_property}` expects `{expected_type}`, got `{type(end_value).__name__}`.")

    ease_fn = EASING_MAP.get(easing, ease_linear)
    return CoshUI._tween_manager.create_tween(n_property, target_id, end_value, duration, ease_fn, path, lerp_fn)