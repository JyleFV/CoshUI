from dataclasses import dataclass

from .engine import CoshUI
from .cui_error import CoshUIError
from .utility import get_node
from .nodes import Element, TextNode
from .types import RenderContext
from ._defaults import *

# ======================== Widgets ========================

# NOTE: Conditional UI is partially unsupported. It's possible, just don't forget to explicitly add ids to all UI elements that appear within conditionals.
@dataclass
class Button(TextNode):
    def __post_init__(self):
        super().__post_init__() # I didn't implement this at first and it broke my shit lol
        if self.font is None:
            self.font = CoshUI._default_font

        # Default style
        if self.text is None:
            raise CoshUIError("Expected text for `Button` widget. Use `Button(text='your text')` with the keyword argument.")
        if self.width == 0.0 and self.layout.width == 0.0:
            self.layout.width = BUTTON_DEFAULT_STYLE["width"]
        if self.height == 0.0 and self.layout.height == 0.0:
            self.layout.height = BUTTON_DEFAULT_STYLE["height"]
        if self.style.background_color is None:
            self.style.background_color = BUTTON_DEFAULT_STYLE["background_color"]
        if self.style.border is None:
            self.style.border = BUTTON_DEFAULT_STYLE["border"]
        if self.style.border_radius == 0:
            self.style.border_radius = BUTTON_DEFAULT_STYLE["border_radius"]
        if self.font_size is None:
            self.font_size = BUTTON_DEFAULT_STYLE["font_size"]
        if self.id is None:
            auto_id = f"_{hash(self.text)}_{CoshUI._widget_counter}"
            self.id = auto_id
            CoshUI._widget_counter += 1
            self._register_id(auto_id)
        if self.on_hover is None:
            node_id = self.id
            self.on_hover = lambda: _button_default_hover(get_node(node_id))
        if self.on_unhover is None:
            node_id = self.id
            self.on_unhover = lambda: _button_default_unhover(get_node(node_id))
        if self.on_click is None:
            node_id = self.id
            self.on_click = lambda: _button_default_click(get_node(node_id))
        if self.on_release is None:
            node_id = self.id
            self.on_release = lambda: _button_default_release(get_node(node_id))

@dataclass
class Label(TextNode):
    def __post_init__(self):
        super().__post_init__() # I didn't implement this at first and it broke my shit lol
        if self.font is None:
            self.font = CoshUI._default_font

        # Default style
        if self.text is None:
            raise CoshUIError("Expected text for `Label` widget. Use `Label(text='your text')` with the keyword argument.")
        if self.width == 0.0 and self.layout.width == 0.0:
            self.layout.width = LABEL_DEFAULT_STYLE["width"]
        if self.height == 0.0 and self.layout.height == 0.0:
            self.layout.height = LABEL_DEFAULT_STYLE["height"]
        if self.font_size is None:
            self.font_size = LABEL_DEFAULT_STYLE["font_size"]

@dataclass
class InputField(TextNode):
    pass

class Checkbox(TextNode):
    pass

class Dropdown(TextNode):
    pass

class Image(Element):
    pass

# ======================== Widgets ========================