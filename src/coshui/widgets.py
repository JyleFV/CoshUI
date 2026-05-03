from dataclasses import dataclass

from .engine import CoshUI
from .nodes import Element
from .types import RenderContext

# ======================== Default Styles ========================

# ======================== Default Styles ========================

# ======================== Widgets ========================

@dataclass
class Button(Element):
    text : str = ""
    font : str | None = None
    font_size : int = 12
    
    def __post_init__(self):
        super().__post_init__() # I didn't implement this at first and it broke my shit lol
        if self.font is None:
            self.font = CoshUI._default_font

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
            border=self.style.border
        )

@dataclass
class Label(Element):
    pass

@dataclass
class InputField(Element):
    pass

class Checkbox(Element):
    pass

class Checkbox(Element):
    pass

class Image(Element):
    pass

# ======================== Widgets ========================