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