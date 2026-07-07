from __future__ import annotations
from typing import TYPE_CHECKING

from ...backend import CoshBackend
from ...utility import intersect_rect
from ...input import CoshInput
from ...types import CoshTextOverflow
from ...utility import resolve_border_radius, _rotate_point_around

if TYPE_CHECKING:
    from ...types import RenderContext

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

    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect, rotation=0.0):
        if alpha <= 0:
            return

        if clip_rect:
            raylibpy.begin_scissor_mode(int(clip_rect[0]), int(clip_rect[1]), int(clip_rect[2]), int(clip_rect[3]))

        final_color = raylibpy.Color(color[0], color[1], color[2], int(alpha))
        top_left, top_right, bottom_right, bottom_left = resolve_border_radius(border_radius)

        if rotation != 0.0:
            center_x = x + w / 2
            center_y = y + h / 2

            raylibpy.rl_push_matrix()
            raylibpy.rl_translatef(center_x, center_y, 0)
            raylibpy.rl_rotatef(-rotation, 0, 0, 1)
            raylibpy.rl_translatef(-center_x, -center_y, 0)

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
            if border is not None:
                b_color, b_width = border
                b_rl_color = raylibpy.Color(b_color[0], b_color[1], b_color[2], int(alpha))

                _draw_asymmetric_rect(x, y, w, h, top_left, top_right, bottom_right, bottom_left, final_color, b_rl_color, b_width)
            else:
                _draw_asymmetric_rect(x, y, w, h, top_left, top_right, bottom_right, bottom_left, final_color)

        if rotation != 0.0:
            raylibpy.rl_pop_matrix()

        if clip_rect:
            raylibpy.end_scissor_mode()

    def _draw_text(self, text_data, node_x, node_y, node_w, node_h, alpha, rotation, clip_rect, scale):
        node_rect = (node_x, node_y, node_w, node_h) if text_data.text_overflow in (CoshTextOverflow.HIDDEN, CoshTextOverflow.WRAP) else None

        final_clip = clip_rect
        if node_rect:
            final_clip = intersect_rect(final_clip, node_rect) if final_clip else node_rect

        if final_clip:
            raylibpy.begin_scissor_mode(int(final_clip[0]), int(final_clip[1]), int(final_clip[2]), int(final_clip[3]))

        node_center = raylibpy.Vector2(node_x + node_w / 2, node_y + node_h / 2)

        for line in text_data.lines:
            for frag in line.fragments:
                scaled_font_size = max(1, int(frag.font_size * scale))
                font = _get_font(frag.font)

                color = raylibpy.Color(frag.color[0], frag.color[1], frag.color[2], alpha)

                frag_x = node_x + frag.x * scale
                frag_y = node_y + line.y * scale
                
                # Get text structural dimensions up front for layout math
                size = raylibpy.measure_text_ex(font, frag.text, scaled_font_size, 1.0)
                frag_w = size.x
                frag_h = size.y
                
                line_thickness = max(1.0, float(scaled_font_size // 16))

                if rotation != 0.0:
                    size = raylibpy.measure_text_ex(font, frag.text, scaled_font_size, 1.0)

                    frag_w = size.x
                    frag_h = size.y

                    frag_center_x = frag_x + (frag_w / 2)
                    frag_center_y = frag_y + (frag_h / 2)

                    
                    new_center_x, new_center_y = _rotate_point_around(frag_center_x, frag_center_y, node_center.x, node_center.y, rotation)

                    raylibpy.draw_text_pro(font, frag.text, raylibpy.Vector2(new_center_x, new_center_y), raylibpy.Vector2(frag_w / 2, frag_h / 2), -rotation, scaled_font_size, 1.0, color)
                
                    if frag.underline:
                        local_line_y = frag_h - 2
                        start_x, start_y = _rotate_point_around(frag_x, frag_y + local_line_y, node_center.x, node_center.y, rotation)
                        end_x, end_y = _rotate_point_around(frag_x + frag_w, frag_y + local_line_y, node_center.x, node_center.y, rotation)
                        raylibpy.draw_line_ex(raylibpy.Vector2(start_x, start_y), raylibpy.Vector2(end_x, end_y), line_thickness, color)
                        
                    if frag.strikethrough:
                        local_line_y = frag_h / 2
                        start_x, start_y = _rotate_point_around(frag_x, frag_y + local_line_y, node_center.x, node_center.y, rotation)
                        end_x, end_y = _rotate_point_around(frag_x + frag_w, frag_y + local_line_y, node_center.x, node_center.y, rotation)
                        raylibpy.draw_line_ex(raylibpy.Vector2(start_x, start_y), raylibpy.Vector2(end_x, end_y), line_thickness, color)
                else:
                    raylibpy.draw_text_ex(font, frag.text, raylibpy.Vector2(frag_x, frag_y), scaled_font_size, 1.0, color)

                    if frag.underline:
                        line_y = frag_y + frag_h - 2
                        raylibpy.draw_line_ex(raylibpy.Vector2(frag_x, line_y), raylibpy.Vector2(frag_x + frag_w, line_y), line_thickness, color)
                        
                    if frag.strikethrough:
                        line_y = frag_y + frag_h / 2
                        raylibpy.draw_line_ex(raylibpy.Vector2(frag_x, line_y), raylibpy.Vector2(frag_x + frag_w, line_y), line_thickness, color)

        if final_clip:
            raylibpy.end_scissor_mode()

    def _draw_image(self, img_path, x, y, w, h, alpha, clip_rect, rotation):
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
        dst_rect = raylibpy.Rectangle(x + w / 2, y + h / 2, w, h)
        origin = raylibpy.Vector2(w / 2, h / 2)
        raylib_rotation = -rotation
        color = raylibpy.Color(255, 255, 255, int(alpha))
        raylibpy.draw_texture_pro(texture, src_rect, dst_rect, origin, raylib_rotation, color)

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
                self._draw_rect(true_x, true_y, scaled_w, scaled_h, data.background_color, data.border_radius, data.alpha, data.border, data.clip_rect, data.transform_rotation)
            
            if data.image_src:
                self._draw_image(data.image_src, true_x, true_y, scaled_w, scaled_h, data.alpha, data.clip_rect, data.transform_rotation)

            if data.text_data:
                self._draw_text(data.text_data, true_x, true_y, scaled_w, scaled_h, data.alpha, data.transform_rotation, data.clip_rect, scale)

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

    def measure_text(self, text_data) -> tuple:
        if not text_data.runs:
            return (0, 0)

        FONT_LOAD_SIZE = 128

        total_width = 0
        max_height = 0

        for run in text_data.runs:
            font_size = run.font_size or 16

            cache_key = run.font
            font = _font_cache.get(cache_key)

            if font is None:
                font = raylibpy.load_font_ex(run.font, FONT_LOAD_SIZE, None, 0)
                raylibpy.set_texture_filter(font.texture, raylibpy.TEXTURE_FILTER_BILINEAR)
                _font_cache[cache_key] = font

            size = raylibpy.measure_text_ex(font, run.text, font_size, 1.0)

            total_width += size.x
            max_height = max(max_height, size.y)

        return (int(total_width), int(max_height))

    def measure_run(self, font_path, font_size, text):
        FONT_LOAD_SIZE = 128

        cache_key = font_path
        font = _font_cache.get(cache_key)

        if font is None:
            font = raylibpy.load_font_ex(font_path, FONT_LOAD_SIZE, None, 0)
            raylibpy.set_texture_filter(font.texture, raylibpy.TEXTURE_FILTER_BILINEAR)
            _font_cache[cache_key] = font

        size = raylibpy.measure_text_ex(font, text, font_size, 1.0)
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
    
    top_left_rounded = round(top_left)
    top_right_rounded = round(top_right)
    bottom_right_rounded = round(bottom_right)
    bottom_left_rounded = round(bottom_left)

    if top_left > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + top_left_rounded, y + top_left_rounded), top_left_rounded, 180, 270, segments, color)
    if top_right > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + w - top_right_rounded, y + top_right_rounded), top_right_rounded, 270, 360, segments, color)
    if bottom_right > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + w - bottom_right_rounded, y + h - bottom_right_rounded), bottom_right_rounded, 0, 90, segments, color)
    if bottom_left > 0:
        raylibpy.draw_circle_sector(raylibpy.Vector2(x + bottom_left_rounded, y + h - bottom_left_rounded), bottom_left_rounded, 90, 180, segments, color)

    top_h = max(top_left_rounded, top_right_rounded)
    if w - top_left_rounded - top_right_rounded > 0 and top_h > 0:
        raylibpy.draw_rectangle(int(x + top_left_rounded), int(y), int(w - top_left_rounded - top_right_rounded), int(top_h), color)

    bot_h = max(bottom_left_rounded, bottom_right_rounded)
    if w - bottom_left_rounded - bottom_right_rounded > 0 and bot_h > 0:
        raylibpy.draw_rectangle(int(x + bottom_left_rounded), int(y + h - bot_h), int(w - bottom_left_rounded - bottom_right_rounded), int(bot_h), color)

    mid_y = y + max(top_left_rounded, top_right_rounded)
    mid_h = h - max(top_left_rounded, top_right_rounded) - max(bottom_left_rounded, bottom_right_rounded)
    if mid_h > 0:
        raylibpy.draw_rectangle(int(x), int(mid_y), int(w), int(mid_h), color)

def _get_font(font_path, load_size=128):
    cache_key = font_path

    font = _font_cache.get(cache_key)

    if font is None:
        font = raylibpy.load_font_ex(font_path, load_size, None, 0)
        raylibpy.set_texture_filter(font.texture, raylibpy.TEXTURE_FILTER_BILINEAR)
        _font_cache[cache_key] = font

    return font

# endregion