from dataclasses import dataclass
import os

from .engine import CoshUI
from .cui_error import CoshUIError, warn
from .types import RenderContext
from .nodes import Element, TextNode
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

        if self.on_hover is None:
            self.on_hover = lambda: _button_default_hover(self.id) # TODO ALL 4 HERE
        if self.on_unhover is None:
            self.on_unhover = lambda: _button_default_unhover(self.id)
        if self.on_click is None:
            self.on_click = lambda: _button_default_click(self.id)
        if self.on_release is None:
            self.on_release = lambda: _button_default_release(self.id)

        super().__post_init__()

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
class Dropdown(TextNode):
    pass

@dataclass
class Slider(Element):
    pass

@dataclass
class Checkbox(Element):
    """ NOTE: Checkboxes don't support background_color animations as background_color is a direct representation of it's functional state """
    checked : bool =  False
    checked_color : tuple | None = None
    unchecked_color : tuple | None = None

    def __post_init__(self):
        if self.id is None:
            raise CoshUIError("Widget `Checkbox` has to have an id.")

        if self.on_click is None:
            self.on_click = lambda: _checkbox_default_click(self.id)

        super().__post_init__()       

        stored_checked = CoshUI.get_state(self.id, "checked")
        if stored_checked is not None:
            self.checked = stored_checked
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

# ======================== Widgets ========================


