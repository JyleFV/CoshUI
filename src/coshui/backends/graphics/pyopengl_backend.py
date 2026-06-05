import numpy as np

from ...backend import CoshBackend
from .gl_window_drivers import Windower

try:
    import OpenGL
except ImportError:
    OpenGL = None

class PyOpenGLBackend(CoshBackend):
    def __init__(self, context, driver : Windower):
        if OpenGL is None:
            raise ImportError(
                "ModernGL (and ModernGLWindow) is not installed. Please install it using `pip install coshui[moderngl]`."
            )
        self.context = context
        self.driver = driver.value()

        self._orthographic_matrix = None
        self._cached_size = (0, 0)

    def _draw_rect(self):
        pass

    def _draw_text(self):
        pass

    def _draw_image(self):
        pass

    def flush(self):
        pass

    def get_size(self):
        return self.driver._get_size()
    
    def poll_input(self):
        return self.driver._poll_input()
    
    def measure_text(self, text, font_path, font_size):
        return self.driver._measure_text(text, font_path, font_size)
    
    def _get_orthographic_matrix(self) -> np.ndarray:
        current_size = self.get_size()
        
        if self._orthographic_matrix is None or current_size != self._cached_size:
            width, height = current_size
            self._orthographic_matrix = np.array([
                2.0 / width, 0.0, 0.0, 0.0,
                0.0, -2.0 / height, 0.0, 0.0,
                0.0, 0.0, -1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0
            ], dtype=np.float32)
            self._cached_size = current_size
        
        return self._orthographic_matrix

    def _get_rect_vertices(self, x, y, width, height):
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
            left, bottom
        ], dtype=np.float32)