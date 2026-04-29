from ..backend import CoshBackend
from ..types import RenderRect

try:
    import pygame
except ImportError:
    pygame = None

class PygameBackend(CoshBackend):
    def __init__(self, surface):
        if pygame is None:
            raise ImportError(
                "Pygame is not installed. Please install it using `pip install coshui[pygame]`."
            )
        self.surface = surface

    def draw_rect(self, x, y, w, h, color):
        pygame.draw.rect(self.surface, color, (x, y, w, h))

    def flush(self, render_stack : list[RenderRect]):
        for data in render_stack:
            self.draw_rect(data.x + data.transform_x, data.y + data.transform_y, data.width, data.height, data.background_color)