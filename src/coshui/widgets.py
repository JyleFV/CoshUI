from .nodes import Element
from .types import RenderRect

class Button(Element):
    text : str = ""

    def get_render_data(self):
        return RenderRect(
            x=self.layout.true_position.x,
            y=self.layout.true_position.y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color.get_tuple(),
            z_index=self.z_index,
            transform_x=self.style.transform_position.x,
            transform_y=self.style.transform_position.y,
        )

class Label(Element):
    pass

class InputField(Element):
    pass

class Checkbox(Element):
    pass
