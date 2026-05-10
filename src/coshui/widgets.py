from dataclasses import dataclass
import os

from .engine import CoshUI
from .cui_error import CoshUIError, warn
from .types import RenderContext, _expand_slider, _expand_dropdown, _expand_modal
from .nodes import Element, TextNode, Modal
from .utility import Ref
from ._defaults import _button_default_click, _button_default_hover, _button_default_release, _button_default_unhover, _checkbox_default_click

# ======================== Widgets ========================

# NOTE: Conditional UI is partially unsupported. It's possible, just don't forget to explicitly add ids to all UI elements that appear within conditionals.
@dataclass
class Button(TextNode):
    def __post_init__(self):
        if self.id is None:
            warn("Please keep in mind to add ids to nodes. It's not required (for some nodes) but it's best practice.")
            auto_id = f"_{hash(__class__)}_{CoshUI._widget_counter}"
            self.id = auto_id
            CoshUI._widget_counter += 1

        if self.font is None:
            self.font = CoshUI._default_font

        super().__post_init__()

        if CoshUI._get_signal(self.id, "hover_enter"):
            _button_default_hover(self.id)
        if CoshUI._get_signal(self.id, "hover_exit"):
            _button_default_unhover(self.id)
        if CoshUI._get_signal(self.id, "clicked"):
            _button_default_click(self.id)
        if CoshUI._get_signal(self.id, "released"):
            _button_default_release(self.id)

@dataclass
class Label(TextNode):
    def __post_init__(self):
        if self.id is None:
            warn("Please keep in mind to add ids to nodes. It's not required (for some nodes) but it's best practice.")
            auto_id = f"_{hash(self.text)}_{CoshUI._widget_counter}"
            self.id = auto_id
            CoshUI._widget_counter += 1
        
        if self.font is None:
            self.font = CoshUI._default_font

        super().__post_init__()

@dataclass
class InputField(TextNode):
    pass

@dataclass
class Checkbox(Element):
    """ NOTE: Checkboxes don't support background_color animations as background_color is a direct representation of it's functional state """
    checked : bool =  False
    checked_color : tuple | None = None
    unchecked_color : tuple | None = None
    bind : Ref | None = None

    def __post_init__(self):
        if self.id is None:
            raise CoshUIError("Widget `Checkbox` has to have an id.")

        if CoshUI._get_signal(self.id, "clicked"):
            _checkbox_default_click(self.id)

        super().__post_init__()       

        stored_checked = CoshUI.get_state(self.id, "checked")
        if stored_checked is not None:
            self.checked = stored_checked
            if self.bind is not None:
                self.bind.value = self.checked
        else:
            CoshUI.set_state(self.id, "checked", self.checked)

    def get_render_data(self):
        return RenderContext(**self.get_base_render_data())

@dataclass
class Image(Element):
    src : str | None = None
    
    def __post_init__(self):
        if self.src:
            self.src = os.path.abspath(self.src)
            if not os.path.isfile(self.src):
                raise CoshUIError(f"Image path `{self.src}` does not exist or is not a file.")
        else:
            raise CoshUIError(f"Expected path value in `src` field.")
        
        super().__post_init__()

    def get_render_data(self):
        data = self.get_base_render_data()
        data["image_src"] = self.src
        return RenderContext(**data)

# Literally just a filler datatype
@dataclass
class Box(Element):
    def get_render_data(self):
        return RenderContext(**self.get_base_render_data())

# ======================== Atomic Widgets ========================

# ======================== Composite Widgets ========================

@dataclass
class Dropdown(TextNode):
    pass

@dataclass
class Slider(Element):
    min_value : float = 0.0
    max_value : float = 100.0
    step : float = 1.0
    value : float | None = None
    bind : Ref | None = None
    thumb_size : int | None = None
    thumb_color : tuple | None = None
    track_color : tuple | None = None
    
    def __post_init__(self):
        if self.id is None:
            raise CoshUIError("Slider must have an id.")
        
        super().__post_init__()

        value = CoshUI.get_state(self.id, "value")
        if value is None:
            value = self.value if self.value is not None else (self.bind.value if self.bind is not None else self.min_value)
            value = max(self.min_value, min(self.max_value, value))
            CoshUI.set_state(self.id, "value", value)
            if self.bind is not None:
                self.bind.value = float(value)

    def get_render_data(self):
        return None

CoshUI._expander_registry[Slider] = _expand_slider
CoshUI._expander_registry[Dropdown] = _expand_dropdown
CoshUI._expander_registry[Modal] = _expand_modal