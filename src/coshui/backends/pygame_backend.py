from ..backend import CoshBackend
from ..types import RenderContext, CoshTextAlign, CoshTextJustify
from ..utility import resolve_border_radius
from ..cui_error import CoshUIError
from ..input import CoshInput

try:
    import pygame
except ImportError:
    pygame = None

_image_cache = {}
_font_cache = {}

class PygameBackend(CoshBackend):
    def __init__(self, surface):
        if pygame is None:
            raise ImportError(
                "Pygame is not installed. Please install it using `pip install coshui[pygame]`."
            )
        self.surface = surface

    # Create a context manager to hold all these values so it's not so messy.
    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border):
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
                    border_bottom_left_radius=int(bl),
                )
                if border is not None:
                    border_color, border_width = border
                    pygame.draw.rect(temp, border_color, (0, 0, w, h), border_width,
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
                    border_bottom_left_radius=int(bl),
                )
                if border is not None:
                    border_color, border_width = border
                    pygame.draw.rect(self.surface, border_color, (x, y, w, h), border_width,
                        border_top_left_radius=int(tl),
                        border_top_right_radius=int(tr),
                        border_bottom_right_radius=int(br),
                        border_bottom_left_radius=int(bl),               
                    )
        except ValueError:
            raise CoshUIError(f"Value in border radius is the wrong type")

    def _draw_text(self, text, x, y, w, h, font_path, font_size, scale, color, align, justify):
        scaled_font_size = max(1, int(font_size * scale))
        cache_key = (font_path, scaled_font_size)
        font = _font_cache.get(cache_key)
        if font is None:
            font = pygame.font.Font(font_path, scaled_font_size)
            _font_cache[cache_key] = font

        text_surface = font.render(text, True, color)
        text_w, text_h = text_surface.get_size()

        match justify:
            case CoshTextJustify.LEFT:
                text_x = x
            case CoshTextJustify.CENTER:
                text_x = x + (w / 2) - (text_w / 2)
            case CoshTextJustify.RIGHT:
                text_x = x + w - text_w

        match align:
            case CoshTextAlign.TOP:
                text_y = y
            case CoshTextAlign.CENTER:
                text_y = y + (h / 2) - (text_h / 2)
            case CoshTextAlign.BOTTOM:
                text_y = y + h - text_h

        self.surface.blit(text_surface, (text_x, text_y))

    def _draw_image(self):
        pass

    def flush(self, render_stack : list[RenderContext]):
        from ..engine import CoshUI

        if CoshUI._temp_paths:
            for path in CoshUI._temp_paths:
                image = pygame.image.load(path).convert_alpha()
                _image_cache[path] = image
            CoshUI._temp_paths.clear()

        # TODO: add font paths from CoshUI._temp_fonts and put it in _font_cache.

        for data in render_stack:
            scale = data.transform_scale
            scaled_w = data.width * scale
            scaled_h = data.height * scale
            offset_x = (data.width - scaled_w) / 2
            offset_y = (data.height - scaled_h) / 2
            true_x = data.x + data.transform_x + offset_x
            true_y = data.y + data.transform_y + offset_y

            self._draw_rect(true_x, true_y, scaled_w, scaled_h, data.background_color, data.border_radius, data.alpha, data.border)
            
            if data.text:
                self._draw_text(data.text, true_x, true_y, scaled_w, scaled_h, data.font, data.font_size, scale, data.text_color, data.text_align, data.text_justify)

    def get_size(self) -> tuple[int, int]:
        return pygame.display.get_surface().get_size()
    
    def poll_input(self):
        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = pygame.mouse.get_pos()
        CoshInput._current_mouse_pressed = pygame.mouse.get_pressed()[0]