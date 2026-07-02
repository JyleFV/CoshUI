from __future__ import annotations
from typing import TYPE_CHECKING

from ...backend import CoshBackend
from ...types import CoshTextOverflow
from ...utility import resolve_border_radius, _rotate_point_around
from ...input import CoshInput

if TYPE_CHECKING:
    from ...types import RenderContext

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

    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect, rotation):
        if alpha <= 0:
            return

        if clip_rect:
            self.surface.set_clip(pygame.Rect(*clip_rect))

        tl, tr, br, bl = resolve_border_radius(border_radius)
        
        use_temp_surface = (alpha < 255) or (rotation and rotation != 0.0)

        if use_temp_surface:
            temp = pygame.Surface((w, h), pygame.SRCALPHA)

            fill_color = (*color, alpha) if alpha < 255 else color
            
            pygame.draw.rect(temp, fill_color, (0, 0, w, h),
                border_top_left_radius=int(tl),
                border_top_right_radius=int(tr),
                border_bottom_right_radius=int(br),
                border_bottom_left_radius=int(bl),
            )
            if border is not None:
                border_color, border_width = border
                final_b_color = (*border_color, alpha) if alpha < 255 else border_color
                pygame.draw.rect(temp, final_b_color, (0, 0, w, h), border_width,
                    border_top_left_radius=int(tl),
                    border_top_right_radius=int(tr),
                    border_bottom_right_radius=int(br),
                    border_bottom_left_radius=int(bl)
                )

            final_x, final_y = x, y
            finalized_surface = temp
            if rotation and rotation != 0:
                finalized_surface = pygame.transform.rotate(temp, rotation)

                center_x = x + (w / 2)
                center_y = y + (h / 2)

                rotated_width, rotated_height = finalized_surface.get_size()

                final_x = center_x - (rotated_width / 2)
                final_y = center_y - (rotated_height / 2)
            else:
                finalized_surface = temp
                final_x, final_y = x, y
                    
            self.surface.blit(finalized_surface, (final_x, final_y))
                
        else:
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

    def _draw_text(self, text_data, node_x, node_y, node_w, node_h, alpha, rotation, clip_rect, scale):
        node_rect = pygame.Rect(node_x, node_y, node_w, node_h) if text_data.text_overflow in (CoshTextOverflow.HIDDEN, CoshTextOverflow.WRAP) else None
        container_rect = pygame.Rect(*clip_rect) if clip_rect else None

        node_center_x = node_x + (node_w / 2)
        node_center_y = node_y + (node_h / 2)

        final_rect = None
        if container_rect and node_rect:
            final_rect = container_rect.clip(node_rect)
        elif container_rect:
            final_rect = container_rect
        elif node_rect:
            final_rect = node_rect

        self.surface.set_clip(final_rect)

        for line in text_data.lines:
            for frag in line.fragments:
                scaled_font_size = max(1, int(frag.font_size * scale))
                font = _get_font(frag.font, scaled_font_size)
                surface = font.render(frag.text, True, frag.color)
                surface.set_alpha(alpha)

                frag_x = node_x + frag.x * scale
                frag_y = node_y + line.y * scale

                if rotation != 0.0:
                    frag_w, frag_h = surface.get_size()

                    fx_center = frag_x + frag_w / 2
                    fy_center = frag_y + frag_h / 2

                    new_center_x, new_center_y = _rotate_point_around(fx_center, fy_center, node_center_x, node_center_y, rotation)

                    rotated_surface = pygame.transform.rotate(surface, rotation)
                    rw, rh = rotated_surface.get_size()
                    final_x = new_center_x - rw / 2
                    final_y = new_center_y - rh / 2
                    self.surface.blit(rotated_surface, (final_x, final_y))
                else:
                    self.surface.blit(surface, (frag_x, frag_y))

        self.surface.set_clip(None)

    def _draw_image(self, img_path, x ,y, w, h, alpha, clip_rect, rotation):
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
        finalized_image = scaled_image
        if rotation != 0.0:
            finalized_image = pygame.transform.rotate(scaled_image, rotation)
        if alpha < 255:
            scaled_image.set_alpha(alpha)

        self.surface.blit(finalized_image, (x, y))

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
                self._draw_rect(true_x, true_y, scaled_w, scaled_h, data.background_color, data.border_radius, data.alpha, data.border, data.clip_rect, data.transform_rotation)
            
            if data.text_data:
                self._draw_text(data.text_data, true_x, true_y, scaled_w, scaled_h, data.alpha, data.transform_rotation, data.clip_rect, scale)

            if data.image_src:
                self._draw_image(data.image_src, true_x, true_y, scaled_w, scaled_h, data.alpha, data.clip_rect, data.transform_rotation)

    def get_size(self) -> tuple[int, int]:
        return pygame.display.get_surface().get_size()
    
    def poll_input(self):
        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = pygame.mouse.get_pos()
        CoshInput._mouse_delta = pygame.mouse.get_rel()
        CoshInput._prev_mouse_position = CoshInput._mouse_position
        CoshInput._current_mouse_pressed = pygame.mouse.get_pressed()[0]

    def measure_text(self, text_data) -> tuple:
        if not text_data.runs:
            return (0, 0)
        
        total_width = 0
        max_height = 0
        
        for run in text_data.runs:
            font = _get_font(run.font, run.font_size)
        
            width, height = font.size(run.text)
        
            total_width += width
            max_height = max(height, max_height)
        
        return (total_width, max_height)
    
    def measure_run(self, font_path, font_size, text):
        font = _get_font(font_path, font_size)
        return font.size(text)
    
def _get_font(font_path, font_size):
    cache_key = (font_path, font_size)
    font = _font_cache.get(cache_key)
    if font is None:
        font = pygame.font.Font(font_path, font_size)
        _font_cache[cache_key] = font
    return font