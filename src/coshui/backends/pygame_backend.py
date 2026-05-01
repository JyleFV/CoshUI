from ..backend import CoshBackend
from ..types import RenderContext
from ..utility import resolve_border_radius
from ..cui_error import CoshUIError

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

    # Create a context manager to hold all these values so it's not so messy.
    def _draw_rect(self, x, y, w, h, color, border_radius, alpha):
        try:
            if color is None:
                return
            
            if alpha <= 0:
                return

            tl, tr, br, bl = resolve_border_radius(border_radius)
            
            if alpha < 255:
                # Create a temporary surface with per-pixel alpha
                temp = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(temp, (*color, alpha), (0, 0, w, h),
                    border_top_left_radius=int(tl),
                    border_top_right_radius=int(tr),
                    border_bottom_right_radius=int(br),
                    border_bottom_left_radius=int(bl)
                )
                self.surface.blit(temp, (x, y))
            else:
                # No alpha, draw directly for performance
                pygame.draw.rect(self.surface, color, (x, y, w, h),
                    border_top_left_radius=int(tl),
                    border_top_right_radius=int(tr),
                    border_bottom_right_radius=int(br),
                    border_bottom_left_radius=int(bl)
                )
        except ValueError:
            raise CoshUIError(f"Value in border radius is the wrong type")

    def flush(self, render_stack : list[RenderContext]):
        for data in render_stack:
            self._draw_rect(data.x + data.transform_x, data.y + data.transform_y, data.width, data.height, data.background_color, data.border_radius, data.alpha)

    def get_size(self) -> tuple[int, int]:
        return pygame.display.get_surface().get_size()