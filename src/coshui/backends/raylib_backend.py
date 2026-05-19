from __future__ import annotations
from typing import TYPE_CHECKING

from ..backend import CoshBackend

from ..input import CoshInput
from ..types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from ..utility import resolve_border_radius

if TYPE_CHECKING:
    from ..types import RenderContext

try:
    import raylibpy
except ImportError:
    raylibpy = None

_image_cache = {}
_font_cache = {}

class RaylibBackend(CoshBackend):
    def __init__(self):
        if raylibpy is None:
            raise ImportError("raylibpy is not installed.")

    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect):
        if alpha <= 0:
            return
        
        if clip_rect:
            raylibpy.begin_scissor_mode(int(clip_rect[0]), int(clip_rect[1]), int(clip_rect[2]), int(clip_rect[3]))

        final_color = raylibpy.Color(color[0], color[1], color[2], int(alpha))
        top_left, top_right, bottom_right, bottom_left = resolve_border_radius(border_radius)

        if top_left == top_right == bottom_right == bottom_left:
            rect = raylibpy.Rectangle(x, y, w, h)
            roundness = 0.0
            if top_left > 0 and min(w, h) > 0:
                roundness = min((top_left * 2) / min(w, h), 1.0)

            if roundness > 0:
                raylibpy.draw_rectangle_rounded(rect, roundness, 16, final_color)
                if border is not None:
                    b_color, b_width = border
                    b_rl_color = raylibpy.Color(b_color[0], b_color[1], b_color[2], int(alpha))
                    raylibpy.draw_rectangle_rounded_lines_ex(rect, roundness, 16, b_width, b_rl_color)
            else:
                raylibpy.draw_rectangle(int(x), int(y), int(w), int(h), final_color)
                if border is not None:
                    b_color, b_width = border
                    b_rl_color = raylibpy.Color(b_color[0], b_color[1], b_color[2], int(alpha))
                    raylibpy.draw_rectangle_lines_ex(rect, b_width, b_rl_color)
        else:
            _draw_asymmetric_rect(x, y, w, h, top_left, top_right, bottom_right, bottom_left, final_color)
            if border is not None:
                b_color, b_width = border
                b_rl_color = raylibpy.Color(b_color[0], b_color[1], b_color[2], int(alpha))
                _draw_asymmetric_rect(x, y, w, h, top_left, top_right, bottom_right, bottom_left, final_color, b_rl_color, b_width)

        if clip_rect:
            raylibpy.end_scissor_mode()


    def _draw_text(self, text, x, y, w, h, font_path, font_size, scale, color, align, justify, clip_rect, text_clip, alpha):
        FONT_LOAD_SIZE = 128

        safe_font_size = font_size if font_size is not None else 16
        safe_scale = scale if scale is not None else 1.0
        scaled_font_size = max(1, int(safe_font_size * safe_scale))

        cache_key = font_path
        font = _font_cache.get(cache_key)
        if font is None:
            font = raylibpy.load_font_ex(font_path, FONT_LOAD_SIZE, None, 0)
            raylibpy.set_texture_filter(font.texture, raylibpy.TEXTURE_FILTER_BILINEAR)
            _font_cache[cache_key] = font
            
        r, g, b = color
        rl_color = raylibpy.Color(r, g, b, int(alpha))
        spacing = 1.0

        text_size = raylibpy.measure_text_ex(font, text, scaled_font_size, spacing)
        text_w, text_h = text_size.x, text_size.y

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

        # Clipping
        final_clip = None
        if clip_rect:
            final_clip = clip_rect
        if text_clip == CoshTextOverflow.HIDDEN:
            node_rect = (x, y, w, h)
            if final_clip:
                from ..utility import intersect_rect
                final_clip = intersect_rect(final_clip, node_rect)
            else:
                final_clip = node_rect

        if final_clip:
            raylibpy.begin_scissor_mode(int(final_clip[0]), int(final_clip[1]), int(final_clip[2]), int(final_clip[3]))

        raylibpy.draw_text_ex(font, text, raylibpy.Vector2(text_x, text_y), scaled_font_size, spacing, rl_color)

        if final_clip:
            raylibpy.end_scissor_mode()


    def _draw_image(self, img_path, x, y, w, h, alpha, clip_rect):
        if alpha <= 0:
            return

        cache_key = img_path
        texture = _image_cache.get(cache_key)
        if texture is None:
            texture = raylibpy.load_texture(img_path)
            _image_cache[cache_key] = texture

        if clip_rect:
            raylibpy.begin_scissor_mode(int(clip_rect[0]), int(clip_rect[1]), int(clip_rect[2]), int(clip_rect[3]))

        src_rect = raylibpy.Rectangle(0, 0, texture.width, texture.height)
        dst_rect = raylibpy.Rectangle(x, y, w, h)
        color = raylibpy.Color(255, 255, 255, int(alpha))
        raylibpy.draw_texture_pro(texture, src_rect, dst_rect, raylibpy.Vector2(0, 0), 0.0, color)

        if clip_rect:
            raylibpy.end_scissor_mode()
    
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

    def get_size(self):
        return (raylibpy.get_screen_width(), raylibpy.get_screen_height())

    def poll_input(self):
        mouse_pos = raylibpy.get_mouse_position()
        mouse_delta = raylibpy.get_mouse_delta()

        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = (int(mouse_pos.x), int(mouse_pos.y))
        CoshInput._mouse_delta = (int(mouse_delta.x), int(mouse_delta.y))
        CoshInput._prev_mouse_position = CoshInput._mouse_position
        CoshInput._current_mouse_pressed = raylibpy.is_mouse_button_down(raylibpy.MOUSE_BUTTON_LEFT)

    def measure_text(self, text, font_path, font_size):
        cache_key = (font_path, font_size)
        font = _font_cache.get(cache_key)
        if font is None:
            font = raylibpy.load_font(font_path)
            _font_cache[cache_key] = font
        
        size = raylibpy.measure_text_ex(font, text, font_size, 0)
        return (int(size.x), int(size.y))

# region: HELPERS

def _draw_asymmetric_rect(x, y, w, h, top_left, top_right, bottom_right, bottom_left, color, border=None, border_width=0):
    top_left = min(top_left, w / 2, h / 2)
    top_right = min(top_right, w / 2, h / 2)
    bottom_right = min(bottom_right, w / 2, h / 2)
    bottom_left = min(bottom_left, w / 2, h / 2)

    # Draw border first (expanded rect in border color)
    if border is not None:
        bx = x - border_width
        by = y - border_width
        bw = w + border_width * 2
        bh = h + border_width * 2
        _draw_asymmetric_rect_filled(bx, by, bw, bh, top_left, top_right, bottom_right, bottom_left, border)

    _draw_asymmetric_rect_filled(x, y, w, h, top_left, top_right, bottom_right, bottom_left, color)

def _draw_asymmetric_rect_filled(x, y, w, h, top_left, top_right, bottom_right, bottom_left, color):
    segments = 16

    if top_left > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + top_left, y + top_left), top_left, 180, 270, segments, color)
    if top_right > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + w - top_right, y + top_right), top_right, 270, 360, segments, color)
    if bottom_right > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + w - bottom_right, y + h - bottom_right), bottom_right, 0, 90, segments, color)
    if bottom_left > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + bottom_left, y + h - bottom_left), bottom_left, 90, 180, segments, color)

    top_h = max(top_left, top_right)
    if w - top_left - top_right > 0 and top_h > 0:
        raylibpy.draw_rectangle(int(x + top_left), int(y), int(w - top_left - top_right), int(top_h), color)

    bot_h = max(bottom_left, bottom_right)
    if w - bottom_left - bottom_right > 0 and bot_h > 0:
        raylibpy.draw_rectangle(int(x + bottom_left), int(y + h - bot_h), int(w - bottom_left - bottom_right), int(bot_h), color)

    mid_y = y + max(top_left, top_right)
    mid_h = h - max(top_left, top_right) - max(bottom_left, bottom_right)
    if mid_h > 0:
        raylibpy.draw_rectangle(int(x), int(mid_y), int(w), int(mid_h), color)