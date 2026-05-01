from .nodes import Element
from .types import RenderContext

class Button(Element):
    text : str = ""
    on_hover : callable | None = None
    on_unhover : callable | None = None
    on_click : callable | None = None
    on_release : callable | None = None

    def get_render_data(self):
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
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
            transform_scale=self.style.transform_scale
        )

class Label(Element):
    pass

class InputField(Element):
    pass

class Checkbox(Element):
    pass

class Image(Element):
    pass
