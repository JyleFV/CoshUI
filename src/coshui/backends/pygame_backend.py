from ..backend import CoshBackend

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