from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path
import ctypes
import numpy as np

from ....backend import CoshBackend
from ....types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from ....utility import resolve_border_radius
from .gl_window_drivers import Windower

if TYPE_CHECKING:
    from ....types import RenderContext

try:
    import OpenGL
    from OpenGL.GL import *
except ImportError:
    OpenGL = None

_texture_cache = {}

class PyOpenGLBackend(CoshBackend):
    def __init__(self, driver: Windower):
        if OpenGL is None:
            raise ImportError(
                "PyOpenGL is not installed. Please install it using `pip install coshui[pyopengl]`."
            )
        self.driver = driver.value()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._orthographic_matrix = None

        # Rect
        self.rect_shader = _load_program("glsl/rect.vert", "glsl/rect.frag")
        self.rect_vbo = _create_vbo()

        # Text
        self.text_shader = _load_program("glsl/text.vert", "glsl/text.frag")
        self.text_vao, self.text_vbo = _create_text_vbo()
        self._atlas_texture_cache = {}

        # Image
        self.image_shader = _load_program("glsl/image.vert", "glsl/image.frag")
        self.image_vbo = _create_vbo()

    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect, rotation):
        if clip_rect:
            cx, cy, cw, ch = clip_rect
            screen_h = self.get_size()[1]
            glEnable(GL_SCISSOR_TEST)
            glScissor(int(cx), int(screen_h - cy - ch), int(cw), int(ch))

        vertices = _get_rect_vertices(x, y, w, h)
        _write_vbo(self.rect_vbo, vertices)

        center_x = x + (w / 2.0)
        center_y = y + (h / 2.0)

        r, g, b = color
        gpu_radius = resolve_border_radius(border_radius)
        half_min = min(w, h) / 2.0
        gpu_radius = tuple(min(float(rad), half_min) for rad in gpu_radius)

        glUseProgram(self.rect_shader)
        _set_uniform_4f(self.rect_shader, 'inColor', r / 255.0, g / 255.0, b / 255.0, alpha / 255.0)
        _set_uniform_2f(self.rect_shader, 'uElementPos', float(x), float(y))
        _set_uniform_2f(self.rect_shader, 'uSize', float(w), float(h))
        _set_uniform_4f(self.rect_shader, 'uRadius', *gpu_radius)

        if border is not None:
            b_color, b_width = border
            _set_uniform_1f(self.rect_shader, 'uBorderWidth', float(b_width))
            _set_uniform_4f(self.rect_shader, 'uBorderColor', b_color[0]/255.0, b_color[1]/255.0, b_color[2]/255.0, alpha/255.0)
        else:
            _set_uniform_1f(self.rect_shader, 'uBorderWidth', 0.0)
            _set_uniform_4f(self.rect_shader, 'uBorderColor', 0.0, 0.0, 0.0, 0.0)

        _set_uniform_1f(self.rect_shader, 'uRotation', rotation)
        _set_uniform_2f(self.rect_shader, 'uCenter', center_x, center_y)
        _set_uniform_matrix4f(self.rect_shader, 'projection', self._get_orthographic_matrix())

        _draw_vbo(self.rect_vbo, self.rect_shader)

        if clip_rect:
            glDisable(GL_SCISSOR_TEST)

    def _draw_text(self, text, x, y, w, h, font_path, font_size, scale, color, align, justify, clip_rect, text_overflow, alpha, rotation):
        from .gl_font import get_atlas, wrap_text, measure_text

        node_clip = (x, y, w, h) if text_overflow in (CoshTextOverflow.HIDDEN, CoshTextOverflow.WRAP) else None
        if clip_rect and node_clip:
            from ....utility import intersect_rect
            final_clip = intersect_rect(clip_rect, node_clip)
        elif node_clip:
            final_clip = node_clip
        else:
            final_clip = clip_rect

        if final_clip:
            cx, cy, cw, ch = final_clip
            screen_h = self.get_size()[1]
            glEnable(GL_SCISSOR_TEST)
            glScissor(int(cx), int(screen_h - cy - ch), int(cw), int(ch))

        safe_font_size = font_size if font_size is not None else 16
        safe_scale = scale if scale is not None else 1.0
        scaled_font_size = max(1, int(safe_font_size * safe_scale))

        atlas = get_atlas(font_path, scaled_font_size)

        atlas_key = (font_path, scaled_font_size)
        gl_atlas = self._atlas_texture_cache.get(atlas_key)
        if gl_atlas is None:
            gl_atlas = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, gl_atlas)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 512, 512, 0, GL_RED, GL_UNSIGNED_BYTE, atlas.texture_data.tobytes())
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            self._atlas_texture_cache[atlas_key] = gl_atlas

        if text_overflow == CoshTextOverflow.WRAP:
            lines = wrap_text(font_path, scaled_font_size, text, w)
        else:
            lines = [text]

        line_height = scaled_font_size
        total_text_h = len(lines) * line_height

        match align:
            case CoshTextAlign.TOP:    start_y = y
            case CoshTextAlign.CENTER: start_y = y + (h / 2) - (total_text_h / 2)
            case CoshTextAlign.BOTTOM: start_y = y + h - total_text_h

        center_x = x + w / 2.0
        center_y = y + h / 2.0

        r, g, b = color
        glUseProgram(self.text_shader)
        _set_uniform_4f(self.text_shader, 'uTextColor', r / 255.0, g / 255.0, b / 255.0, alpha / 255.0)
        _set_uniform_1f(self.text_shader, 'uRotation', rotation)
        _set_uniform_2f(self.text_shader, 'uCenter', center_x, center_y)
        _set_uniform_matrix4f(self.text_shader, 'projection', self._get_orthographic_matrix())
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, gl_atlas)
        _set_uniform_1i(self.text_shader, 'uAtlas', 0)

        for i, line in enumerate(lines):
            line_w, _ = measure_text(font_path, scaled_font_size, line)

            match justify:
                case CoshTextJustify.LEFT:   pen_x = x
                case CoshTextJustify.CENTER: pen_x = x + (w / 2) - (line_w / 2)
                case CoshTextJustify.RIGHT:  pen_x = x + w - line_w

            pen_y = start_y + (i * line_height)
            baseline_y = pen_y + line_height

            vertices = []
            for char in line:
                if char not in atlas.glyphs:
                    continue
                g = atlas.glyphs[char]
                if g.width == 0 or g.height == 0:
                    pen_x += g.advance
                    continue

                x0 = pen_x + g.bitmap_left
                y0 = baseline_y - g.bitmap_top
                x1 = x0 + g.width
                y1 = y0 + g.height

                u0, v0 = g.uv_x, g.uv_y
                u1, v1 = g.uv_x + g.uv_w, g.uv_y + g.uv_h

                vertices.extend([
                    x0, y0, u0, v0,
                    x1, y0, u1, v0,
                    x1, y1, u1, v1,
                    x0, y0, u0, v0,
                    x1, y1, u1, v1,
                    x0, y1, u0, v1,
                ])
                pen_x += g.advance

            if not vertices:
                continue

            vertex_data = np.array(vertices, dtype=np.float32)
            vao, vbo = self.text_vao, self.text_vbo
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_DYNAMIC_DRAW)
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 4)
            glBindVertexArray(0)

        if final_clip:
            glDisable(GL_SCISSOR_TEST)

    def _draw_image(self, img_path, x, y, w, h, alpha, clip_rect, rotation):
        if clip_rect:
            cx, cy, cw, ch = clip_rect
            screen_h = self.get_size()[1]
            glEnable(GL_SCISSOR_TEST)
            glScissor(int(cx), int(screen_h - cy - ch), int(cw), int(ch))

        texture = _texture_cache.get(img_path)
        if texture is None:
            from PIL import Image
            img = Image.open(img_path).convert("RGBA")
            img_data = img.tobytes()
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            _texture_cache[img_path] = texture

        vertices = _get_rect_vertices(x, y, w, h)
        _write_vbo(self.image_vbo, vertices)

        center_x = x + (w / 2.0)
        center_y = y + (h / 2.0)

        glUseProgram(self.image_shader)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        _set_uniform_1i(self.image_shader, 'uTexture', 0)
        _set_uniform_1f(self.image_shader, 'uAlpha', alpha / 255.0)
        _set_uniform_2f(self.image_shader, 'uElementPos', float(x), float(y))
        _set_uniform_2f(self.image_shader, 'uSize', float(w), float(h))
        _set_uniform_1f(self.image_shader, 'uRotation', rotation)
        _set_uniform_2f(self.image_shader, 'uCenter', center_x, center_y)
        _set_uniform_matrix4f(self.image_shader, 'projection', self._get_orthographic_matrix())

        _draw_vbo(self.image_vbo, self.image_shader)

        if clip_rect:
            glDisable(GL_SCISSOR_TEST)

    def flush(self, render_stack: list[RenderContext]):
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

    def get_size(self):
        return self.driver._get_size()

    def poll_input(self):
        return self.driver._poll_input()

    def measure_text(self, text, font_path, font_size):
        from .gl_font import measure_text as ft_measure
        return ft_measure(font_path, font_size, text)

    def _get_orthographic_matrix(self) -> np.ndarray:
        width, height = self.get_size()
        glViewport(0, 0, width, height)
        self._orthographic_matrix = np.array([
            2.0 / width, 0.0, 0.0, 0.0,
            0.0, -2.0 / height, 0.0, 0.0,
            0.0, 0.0, -1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0
        ], dtype=np.float32)
        return self._orthographic_matrix


# region HELPERS

def _load_program(vertex_relative_path: str, fragment_relative_path: str) -> int:
    backend_dir = Path(__file__).parent.resolve()
    vertex_path = (backend_dir / vertex_relative_path).resolve()
    fragment_path = (backend_dir / fragment_relative_path).resolve()

    with open(vertex_path, 'r') as f:
        vertex_source = f.read()
    with open(fragment_path, 'r') as f:
        fragment_source = f.read()

    vert_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vert_shader, vertex_source)
    glCompileShader(vert_shader)
    if not glGetShaderiv(vert_shader, GL_COMPILE_STATUS):
        raise RuntimeError(f"Vertex shader compile error: {glGetShaderInfoLog(vert_shader).decode()}")

    frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(frag_shader, fragment_source)
    glCompileShader(frag_shader)
    if not glGetShaderiv(frag_shader, GL_COMPILE_STATUS):
        raise RuntimeError(f"Fragment shader compile error: {glGetShaderInfoLog(frag_shader).decode()}")

    program = glCreateProgram()
    glAttachShader(program, vert_shader)
    glAttachShader(program, frag_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(f"Shader link error: {glGetProgramInfoLog(program).decode()}")

    glDeleteShader(vert_shader)
    glDeleteShader(frag_shader)

    return program

def _create_vbo() -> tuple:
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, 48, None, GL_DYNAMIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, None)
    glBindVertexArray(0)
    return (vao, vbo)

def _create_text_vbo() -> tuple:
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, 24 * 4 * 128, None, GL_DYNAMIC_DRAW)
    # aPos
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, None)
    # aUV
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
    glBindVertexArray(0)
    return (vao, vbo)

def _write_vbo(vbo_tuple: tuple, vertices: np.ndarray):
    _, vbo = vbo_tuple
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)

def _draw_vbo(vbo_tuple: tuple, program: int):
    vao, _ = vbo_tuple
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, 6)
    glBindVertexArray(0)

def _get_uniform_location(program: int, name: str) -> int:
    return glGetUniformLocation(program, name)

def _set_uniform_1f(program: int, name: str, v: float):
    glUniform1f(_get_uniform_location(program, name), v)

def _set_uniform_1i(program: int, name: str, v: int):
    glUniform1i(_get_uniform_location(program, name), v)

def _set_uniform_2f(program: int, name: str, x: float, y: float):
    glUniform2f(_get_uniform_location(program, name), x, y)

def _set_uniform_4f(program: int, name: str, x: float, y: float, z: float, w: float):
    glUniform4f(_get_uniform_location(program, name), x, y, z, w)

def _set_uniform_matrix4f(program: int, name: str, matrix: np.ndarray):
    glUniformMatrix4fv(_get_uniform_location(program, name), 1, GL_FALSE, matrix)

def _get_rect_vertices(x, y, width, height) -> np.ndarray:
    left, right, top, bottom = x, x + width, y, y + height
    return np.array([
        left, top,
        right, top,
        right, bottom,
        left, top,
        right, bottom,
        left, bottom,
    ], dtype=np.float32)

# endregion