from dataclasses import dataclass
import os

from .engine import CoshUI
from .cui_error import CoshUIError, warn
from .utility import get_node
from .types import RenderContext
from .nodes import Element, TextNode
from ._defaults import _button_default_click, _button_default_hover, _button_default_release, _button_default_unhover, _checkbox_default_click

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
        
        if self.id is None:
            warn("Please keep in mind to add ids to nodes. It's not required (for some nodes) but it's best practice.")
            auto_id = f"_{hash(self.text)}_{CoshUI._widget_counter}"
            self.id = auto_id
            CoshUI._widget_counter += 1
            self._register_id(auto_id)

        if self.width == 0.0 and self.layout.width == 0.0:
            self.layout.width = CoshUI._active_theme.button.get("width")
        if self.height == 0.0 and self.layout.height == 0.0:
            self.layout.height = CoshUI._active_theme.button.get("height")
        if self.style.background_color is None:
            self.style.background_color = CoshUI._active_theme.button.get("background_color")
        if self.style.border is None:
            self.style.border = CoshUI._active_theme.button.get("border")
        if self.style.border_radius == 0:
            self.style.border_radius = CoshUI._active_theme.button.get("border_radius")
        if self.font_size is None:
            self.font_size = CoshUI._active_theme.button.get("font_size")
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
        
        if self.id is None:
            warn("Please keep in mind to add ids to nodes. It's not required (for some nodes) but it's best practice.")
            auto_id = f"_{hash(self.text)}_{CoshUI._widget_counter}"
            self.id = auto_id
            CoshUI._widget_counter += 1
            self._register_id(auto_id)
        
        if self.font is None:
            self.font = CoshUI._default_font

        # Default style
        if self.text is None:
            raise CoshUIError("Expected text for `Label` widget. Use `Label(text='your text')` with the keyword argument.")
        if self.width == 0.0 and self.layout.width == 0.0:
            self.layout.width = CoshUI._active_theme.label.get("width")
        if self.height == 0.0 and self.layout.height == 0.0:
            self.layout.height = CoshUI._active_theme.label.get("height")
        if self.font_size is None:
            self.font_size = CoshUI._active_theme.label.get("font_size")

@dataclass
class InputField(TextNode):
    pass


class Dropdown(TextNode):
    pass

@dataclass
class Checkbox(Element):
    checked : bool =  False

    def __post_init__(self):
        super().__post_init__()

        if self.id is None:
            raise CoshUIError("Widget `Checkbox` has to have an id.")

        from .engine import CoshUI
        existing = CoshUI._node_map.get(self.id)
        
        if existing is not None and isinstance(existing, Checkbox):
            self.style = existing.style
            self.checked = existing.checked
            self._was_hovered = existing._was_hovered
        
        CoshUI._node_map[self.id] = self

        if self.width == 0.0 and self.layout.width == 0.0:
            self.layout.width = CoshUI._active_theme.checkbox.get("width")
        if self.height == 0.0 and self.layout.height == 0.0:
            self.layout.height = CoshUI._active_theme.checkbox.get("height")

        if self.on_click is None:
            node_id = self.id
            self.on_click = lambda: _checkbox_default_click(CoshUI._node_map.get(node_id))

        self._update_visual_state()

    def _update_visual_state(self):
        theme = CoshUI._active_theme.checkbox
        self.style.background_color = theme.get("checked") if self.checked else theme.get("unchecked")

    def get_render_data(self):
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
            id=self.id,
            x=x,
            y=y,
            transform_x=transform_x,
            transform_y=transform_y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color,
            z_index=self.z_index,
            border_radius=self.style.border_radius,
            alpha=self.style.alpha,
            transform_scale=self.style.transform_scale,
            border=self.style.border,
        )

@dataclass
class Image(Element):
    src : str | None = None
    
    def __post_init__(self):
        super().__post_init__()

        if self.width == 0.0 and self.layout.width == 0.0:
            self.layout.width = CoshUI._active_theme.image.get("width")
        if self.height == 0.0 and self.layout.height == 0.0:
            self.layout.height = CoshUI._active_theme.image.get("height") 

        if self.src:
            self.src = os.path.abspath(self.src)
            if not os.path.isfile(self.src):
                raise CoshUIError(f"Image path `{self.src}` does not exist or is not a file.")
        else:
            raise CoshUIError(f"Expected path value in `src` field.")

    def get_render_data(self):
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
            id=self.id,
            x=x,
            y=y,
            transform_x=transform_x,
            transform_y=transform_y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color,
            z_index=self.z_index,
            border_radius=self.style.border_radius,
            alpha=self.style.alpha,
            transform_scale=self.style.transform_scale,
            border=self.style.border,
            image_src=self.src
        )

# ======================== Widgets ========================


