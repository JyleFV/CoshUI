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

        super().__post_init__() # I didn't implement this at first and it broke my shit lol

        # # Default style
        # if self.text is None:
        #     raise CoshUIError("Expected text for `Button` widget. Use `Button(text='your text')` with the keyword argument.")
        
        # if self.id is None:
        #     warn("Please keep in mind to add ids to nodes. It's not required (for some nodes) but it's best practice.")
        #     auto_id = f"_{hash(self.text)}_{CoshUI._widget_counter}"
        #     self.id = auto_id
        #     CoshUI._widget_counter += 1
        #     self._register_id(auto_id)

        # if self.width == 0.0 and self.layout.width == 0.0:
        #     self.layout.width = CoshUI._active_theme.button.get("width")
        # if self.height == 0.0 and self.layout.height == 0.0:
        #     self.layout.height = CoshUI._active_theme.button.get("height")
        # if self.style.background_color is None:
        #     self.style.background_color = CoshUI._active_theme.button.get("background_color")
        # if self.style.border is None:
        #     self.style.border = CoshUI._active_theme.button.get("border")
        # if self.style.border_radius == 0:
        #     self.style.border_radius = CoshUI._active_theme.button.get("border_radius")
        # if self.font_size is None:
        #     self.font_size = CoshUI._active_theme.button.get("font_size")

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
            mouse_filter=self.mouse_filter
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
            image_src=self.src,
            mouse_filter=self.mouse_filter
        )

# ======================== Widgets ========================


