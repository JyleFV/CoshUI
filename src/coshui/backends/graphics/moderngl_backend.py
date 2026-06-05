from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path # Damn didn't know about this, this is good
import numpy as np

from ...backend import CoshBackend
from ...types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from ...utility import resolve_border_radius
from .gl_window_drivers import Windower

if TYPE_CHECKING:
    from ...types import RenderContext

try:
    import moderngl
except ImportError:
    moderngl = None

# NOTE: An optimization route in the future is batching, but I'm not very good at GLSL so I can't make an uber shader that helps with that.
class ModernGLBackend(CoshBackend):
    def __init__(self, context, driver : Windower):
        if moderngl is None:
            raise ImportError(
                "ModernGL (and ModernGLWindow) is not installed. Please install it using `pip install coshui[moderngl]`."
            )
        self.context = context
        self.driver = driver.value()

        self.context.enable(moderngl.BLEND)
        self.context.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        self._orthographic_matrix = None
        self._cached_size = (0, 0)

        self.rect_shader = _load_program(self.context, "glsl/rect.vert", "glsl/rect.frag")
        self.rect_vbo = self.context.buffer(reserve=12 * 4)
        self.rect_vao = self.context.vertex_array(self.rect_shader, [(self.rect_vbo, '2f', 'aPos')])

    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect, rotation):
        if clip_rect:
            self.context.scissor = clip_rect

        vertices = _get_rect_vertices(x, y, w, h)
        self.rect_vbo.write(vertices)

        center_x = x + (w / 2.0)
        center_y = y + (h / 2.0)

        r, g, b = color
        gpu_radius = resolve_border_radius(border_radius)
        half_min = min(w, h) / 2.0
        gpu_radius = tuple(min(float(rad), half_min) for rad in gpu_radius)

        self.rect_shader['inColor'].value = (r / 255.0, g / 255.0, b / 255.0, alpha / 255.0)
        self.rect_shader['uElementPos'].value = (float(x), float(y))
        self.rect_shader['uSize'].value = (float(w), float(h))
        self.rect_shader['uRadius'].value = gpu_radius

        if border is not None:
            b_color, b_width = border
            self.rect_shader['uBorderWidth'].value = float(b_width)
            self.rect_shader['uBorderColor'].value = (b_color[0]/255.0, b_color[1]/255.0, b_color[2]/255.0, alpha/255.0)
        else:
            self.rect_shader['uBorderWidth'].value = 0.0
            self.rect_shader['uBorderColor'].value = (0.0, 0.0, 0.0, 0.0)

        self.rect_shader['uRotation'].value = rotation
        self.rect_shader['uCenter'].value = (center_x, center_y)
        self.rect_shader['projection'].write(self._get_orthographic_matrix())

        self.rect_vao.render(moderngl.TRIANGLES)

        if clip_rect:
            self.context.scissor = None

    def _draw_text(self, text, x, y, w, h, font_path, font_size, scale, color, align, justify, clip_rect, text_overflow, alpha, rotation):
        pass

    def _draw_image(self, img_path, x ,y, w, h, alpha, clip_rect, rotation):
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
    
    def _get_orthographic_matrix(self) -> np.ndarray:
        width, height = self.get_size()
        self.context.viewport = (0, 0, width, height)
        self._orthographic_matrix = np.array([
            2.0 / width, 0.0, 0.0, 0.0,
            0.0, -2.0 / height, 0.0, 0.0,
            0.0, 0.0, -1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0
        ], dtype=np.float32)
        
        return self._orthographic_matrix

# region HELPERS
def _load_program(context, vertex_relative_path: str, fragment_relative_path: str):
    backend_dir = Path(__file__).parent.resolve()

    vertex_path = (backend_dir / vertex_relative_path).resolve()
    fragment_path = (backend_dir / fragment_relative_path).resolve()

    with open(vertex_path, 'r') as f:
        vertex_source = f.read()
        
    with open(fragment_path, 'r') as f:
        fragment_source = f.read()
        
    return context.program(
        vertex_shader=vertex_source,
        fragment_shader=fragment_source
    )

def _get_rect_vertices(x, y, width, height):
    left = x
    right = x + width
    top = y
    bottom = y + height

    return np.array([
        left, top,
        right, top,
        right, bottom,

        left, top,
        right, bottom,
        left, bottom,
    ], dtype=np.float32)

# endregion