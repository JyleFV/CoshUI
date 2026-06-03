from __future__ import annotations
from typing import TYPE_CHECKING

from ...backend import CoshBackend
from ...types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from .gl_window_drivers import Windower

if TYPE_CHECKING:
    from ...types import RenderContext

try:
    import moderngl
except ImportError:
    moderngl = None


class ModernGLBackend(CoshBackend):
    def __init__(self, context, driver : Windower):
        if moderngl is None:
            raise ImportError(
                "ModernGL (and ModernGLWindow) is not installed. Please install it using `pip install coshui[moderngl]`."
            )
        self.context = context
        self.driver = driver.value()

    def _draw_rect(self):
        pass

    def _draw_text(self):
        pass

    def _draw_image(self):
        pass

    def flush(self, render_stack : list[RenderContext]):
        for data in render_stack:
            if data.alpha <= 0:
                continue

            scale = data.transform_scale
            scaled_w = data.width * scale
            scaled_h = data.height * scale
            offset_x = (data.width - scaled_w) / 2
            offset_y = (data.height - scaled_h) / 2
            true_x = data.x + data.transform_x + offset_x
            true_y = data.y + data.transform_y + offset_y

            if data.background_color:
                self._draw_rect(true_x, true_y, scaled_w, scaled_h, data.background_color, data.border_radius, data.alpha, data.border, data.clip_rect, data.transform_rotation)
            
            if data.text:
                self._draw_text(data.text, true_x, true_y, scaled_w, scaled_h, data.font, data.font_size, scale, data.text_color, data.text_align, data.text_justify, data.clip_rect, data.text_overflow, data.alpha, data.transform_rotation)

            if data.image_src:
                self._draw_image(data.image_src, true_x, true_y, scaled_w, scaled_h, data.alpha, data.clip_rect, data.transform_rotation)

    def get_size(self):
        return self.driver._get_size()
    
    def poll_input(self):
        return self.driver._poll_input()
    
    def measure_text(self, text, font_path, font_size):
        return self.driver._measure_text(text, font_path, font_size)
    