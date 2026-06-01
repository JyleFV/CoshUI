from __future__ import annotations
from typing import TYPE_CHECKING

from ...backend import CoshBackend
from ...types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from ...utility import resolve_border_radius
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

    def _draw_text(self, text, x, y, w, h, font_path, font_size, scale, color, align, justify, clip_rect, text_overflow, alpha, rotation):
        safe_font_size = font_size if font_size is not None else 16
        safe_scale = scale if scale is not None else 1.0

        scaled_font_size = max(1, int(safe_font_size * safe_scale))
        cache_key = (font_path, scaled_font_size)
        font = _font_cache.get(cache_key)
        if font is None:
            font = pygame.font.Font(font_path, scaled_font_size)
            _font_cache[cache_key] = font

        if text_overflow is CoshTextOverflow.WRAP:
            lines = []
            words = text.split(' ')
            current_line = ""
            
            for word in words:
                test_line = f"{current_line} {word}".strip() if current_line else word
                test_w, _ = font.size(test_line)
                
                if test_w <= w:
                    current_line = test_line
                else:
                    if not current_line:
                        lines.append(word)
                        current_line = ""
                    else:
                        lines.append(current_line)
                        current_line = word
            if current_line:
                lines.append(current_line)
        else:
            lines = [text]

        line_height = font.get_linesize()
        total_text_h = len(lines) * line_height

        container_rect = pygame.Rect(*clip_rect) if clip_rect else None

        node_rect = pygame.Rect(x, y, w, h) if text_overflow in (CoshTextOverflow.HIDDEN, CoshTextOverflow.WRAP) else None

        final_rect = None
        if container_rect and node_rect:
            final_rect = container_rect.clip(node_rect)
        elif container_rect:
            final_rect = container_rect
        elif node_rect:
            final_rect = node_rect

        self.surface.set_clip(final_rect)

        match align:
            case CoshTextAlign.TOP:
                start_y = y
            case CoshTextAlign.CENTER:
                start_y = y + (h / 2) - (total_text_h / 2)
            case CoshTextAlign.BOTTOM:
                start_y = y + h - total_text_h

        for i, line_text in enumerate(lines):
            line_surface = font.render(line_text, True, color)
            line_surface.set_alpha(alpha)
            line_w, _ = line_surface.get_size()

            match justify:
                case CoshTextJustify.LEFT:
                    text_x = x
                case CoshTextJustify.CENTER:
                    text_x = x + (w / 2) - (line_w / 2)
                case CoshTextJustify.RIGHT:
                    text_x = x + w - line_w
                    
            text_y = start_y + (i * line_height)
            
            final_x, final_y = text_x, text_y
            final_surface = line_surface
            if rotation != 0.0:
                _, line_h = line_surface.get_size()
                center_x = text_x + (line_w / 2)
                center_y = text_y + (line_h / 2)

                final_surface = pygame.transform.rotate(line_surface, rotation)

                rotated_width, rotated_height = final_surface.get_size()

                final_x = center_x - (rotated_width / 2)
                final_y = center_y - (rotated_height / 2)

            self.surface.blit(final_surface, (final_x, final_y))

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
            
            if data.text:
                self._draw_text(data.text, true_x, true_y, scaled_w, scaled_h, data.font, data.font_size, scale, data.text_color, data.text_align, data.text_justify, data.clip_rect, data.text_overflow, data.alpha, data.transform_rotation)

            if data.image_src:
                self._draw_image(data.image_src, true_x, true_y, scaled_w, scaled_h, data.alpha, data.clip_rect, data.transform_rotation)

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