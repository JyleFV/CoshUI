from __future__ import annotations
from typing import TYPE_CHECKING

from ..backend import CoshBackend
from ..types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from ..utility import resolve_border_radius
from ..input import CoshInput

if TYPE_CHECKING:
    from ..types import RenderContext

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
    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect):
        if alpha <= 0:
            return

        if clip_rect:
            self.surface.set_clip(pygame.Rect(*clip_rect))

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
        self.surface.set_clip(None)

    def _draw_text(self, text, x, y, w, h, font_path, font_size, scale, color, align, justify, clip_rect, text_clip, alpha):
        safe_font_size = font_size if font_size is not None else 16
        safe_scale = scale if scale is not None else 1.0

        scaled_font_size = max(1, int(safe_font_size * safe_scale))
        cache_key = (font_path, scaled_font_size)
        font = _font_cache.get(cache_key)
        if font is None:
            font = pygame.font.Font(font_path, scaled_font_size)
            _font_cache[cache_key] = font

        text_surface = font.render(text, True, color)
        text_surface.set_alpha(alpha)
        text_w, text_h = text_surface.get_size()

        # Clipping Logic
        container_rect = pygame.Rect(*clip_rect) if clip_rect else None
        node_rect = pygame.Rect(x, y, w, h) if text_clip is CoshTextOverflow.HIDDEN else None

        final_rect = None

        if container_rect and node_rect:
            final_rect = container_rect.clip(node_rect)
        elif container_rect:
            final_rect = container_rect
        elif node_rect:
            final_rect = node_rect

        self.surface.set_clip(final_rect)

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
        self.surface.set_clip(None)

    def _draw_image(self, img_path, x ,y, w, h, alpha, clip_rect):
        if alpha <= 0:
            return

        if clip_rect:
            self.surface.set_clip(pygame.Rect(*clip_rect))

        cache_key = img_path
        image = _image_cache.get(cache_key)
        if image is None:
            image = pygame.image.load(img_path).convert_alpha()
            _image_cache[cache_key] = image

        scaled_image = pygame.transform.smoothscale(image, (int(w), int(h)))
        if alpha < 255:
            scaled_image.set_alpha(alpha)
        self.surface.blit(scaled_image, (x, y))

        self.surface.set_clip(None)

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
                self._draw_rect(true_x, true_y, scaled_w, scaled_h, data.background_color, data.border_radius, data.alpha, data.border, data.clip_rect)
            
            if data.text:
                self._draw_text(data.text, true_x, true_y, scaled_w, scaled_h, data.font, data.font_size, scale, data.text_color, data.text_align, data.text_justify, data.clip_rect, data.text_overflow, data.alpha)

            if data.image_src:
                self._draw_image(data.image_src, true_x, true_y, scaled_w, scaled_h, data.alpha, data.clip_rect)

    def get_size(self) -> tuple[int, int]:
        return pygame.display.get_surface().get_size()
    
    def measure_text(self, text, font_path, font_size) -> tuple:
        cache_key = (font_path, font_size)
        font = _font_cache.get(cache_key)
        if font is None:
            font = pygame.font.Font(font_path, font_size)
            _font_cache[cache_key] = font
        return font.size(text)

    def poll_input(self):
        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = pygame.mouse.get_pos()
        CoshInput._mouse_delta = pygame.mouse.get_rel()
        CoshInput._prev_mouse_position = CoshInput._mouse_position
        CoshInput._current_mouse_pressed = pygame.mouse.get_pressed()[0]