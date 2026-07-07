from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path # Damn didn't know about this, this is good
import numpy as np

from ....backend import CoshBackend
from ....types import CoshTextAlign, CoshTextJustify, CoshTextOverflow
from ....utility import resolve_border_radius, _rotate_point_around
from .gl_window_drivers import Windower

if TYPE_CHECKING:
    from ....types import RenderContext

try:
    import moderngl
except ImportError:
    moderngl = None

_texture_cache = {}

# NOTE: An optimization route in the future is batching, but I'm not very good at GLSL so I can't make an uber shader that helps with that.
class ModernGLBackend(CoshBackend):
    def __init__(self, context, driver : Windower):
        if moderngl is None:
            raise ImportError(
                "ModernGL is not installed. Please install it using `pip install coshui[moderngl]`."
            )
        self.context = context
        self.driver = driver.value()

        # Automatic enabling of blend mode so border radius and alpha works out the box without the user caring if they forgot
        self.context.enable(moderngl.BLEND)
        self.context.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        
        self._orthographic_matrix = None
        self._cached_size = (0, 0)

        # Rect
        self.rect_shader = _load_program(self.context, "glsl/rect.vert", "glsl/rect.frag")
        self.rect_vbo = self.context.buffer(reserve=12 * 4)
        self.rect_vao = self.context.vertex_array(self.rect_shader, [(self.rect_vbo, '2f', 'aPos')])

        # Text
        self.text_shader = _load_program(self.context, "glsl/text.vert", "glsl/text.frag")
        self.text_vbo = self.context.buffer(reserve=24 * 4 * 128)  # 128 quads max per draw
        self.text_vao = self.context.vertex_array(self.text_shader, [(self.text_vbo, '2f 2f', 'aPos', 'aUV')])
        self._atlas_texture_cache = {}

        # Image
        self.image_shader = _load_program(self.context, "glsl/image.vert", "glsl/image.frag")
        self.image_vbo = self.context.buffer(reserve=12 * 4)
        self.image_vao = self.context.vertex_array(self.image_shader, [(self.image_vbo, '2f', 'aPos')])

    def _draw_rect(self, x, y, w, h, color, border_radius, alpha, border, clip_rect, rotation):
        if clip_rect:
            cx, cy, cw, ch = clip_rect
            screen_h = self.get_size()[1]
            self.context.scissor = (int(cx), int(screen_h - cy - ch), int(cw), int(ch))

        vertices = _get_rect_vertices(x, y, w, h)
        self.rect_vbo.write(vertices)

        center_x = x + (w / 2.0)
        center_y = y + (h / 2.0)

        r, g, b = color
        gpu_radius = resolve_border_radius(border_radius)
        half_min = min(w, h) / 2.0
        gpu_radius = tuple(min(float(rad), half_min) for rad in gpu_radius)

        self.rect_shader['inColor'].value = (r / 255.0, g / 255.0, b / 255.0, alpha / 255.0)
        self.rect_shader['uElementPos'].value = (float(x), float(y))
        self.rect_shader['uSize'].value = (float(w), float(h))
        self.rect_shader['uRadius'].value = gpu_radius

        if border is not None:
            b_color, b_width = border
            self.rect_shader['uBorderWidth'].value = float(b_width)
            self.rect_shader['uBorderColor'].value = (b_color[0]/255.0, b_color[1]/255.0, b_color[2]/255.0, alpha/255.0)
        else:
            self.rect_shader['uBorderWidth'].value = 0.0
            self.rect_shader['uBorderColor'].value = (0.0, 0.0, 0.0, 0.0)

        self.rect_shader['uRotation'].value = rotation
        self.rect_shader['uCenter'].value = (center_x, center_y)
        self.rect_shader['projection'].write(self._get_orthographic_matrix())

        self.rect_vao.render(moderngl.TRIANGLES)

        if clip_rect:
            self.context.scissor = None

    def _draw_text(self, text_data, node_x, node_y, node_w, node_h, alpha, rotation, clip_rect, scale):
        from .gl_font import get_atlas
        from ....utility import intersect_rect

        node_clip = (node_x, node_y, node_w, node_h) if text_data.text_overflow in (CoshTextOverflow.HIDDEN, CoshTextOverflow.WRAP) else None

        if clip_rect and node_clip:
            final_clip = intersect_rect(clip_rect, node_clip)
        elif node_clip:
            final_clip = node_clip
        else:
            final_clip = clip_rect

        if final_clip:
            cx, cy, cw, ch = final_clip
            screen_h = self.get_size()[1]
            self.context.scissor = (int(cx), int(screen_h - cy - ch), int(cw), int(ch))

        center_x = node_x + node_w / 2.0
        center_y = node_y + node_h / 2.0

        self.text_shader["uRotation"].value = rotation
        self.text_shader["uCenter"].value = (center_x, center_y)
        self.text_shader["projection"].write(self._get_orthographic_matrix())

        for line in text_data.lines:
            for frag in line.fragments:
                scaled_font_size = max(1, int(frag.font_size * scale))

                atlas = get_atlas(frag.font, scaled_font_size)

                atlas_key = (frag.font, scaled_font_size)
                gl_atlas = self._atlas_texture_cache.get(atlas_key)

                if gl_atlas is None:
                    gl_atlas = self.context.texture((512, 512), 1, atlas.texture_data.tobytes())
                    gl_atlas.filter = moderngl.LINEAR, moderngl.LINEAR
                    self._atlas_texture_cache[atlas_key] = gl_atlas

                r, g, b = frag.color
                self.text_shader["uTextColor"].value = (
                    r / 255.0,
                    g / 255.0,
                    b / 255.0,
                    alpha / 255.0
                )

                gl_atlas.use(location=0)
                self.text_shader["uAtlas"].value = 0

                pen_x = node_x + frag.x * scale
                pen_y = node_y + line.y * scale
                baseline_y = pen_y + atlas.ascender
                frag_start_x = pen_x

                if frag.underline or frag.strikethrough:
                    frag_w = frag.width * scale
                    frag_h = atlas.ascender + atlas.descender
                    thickness = max(1, int(scaled_font_size // 16))
                    if frag.underline:
                        _draw_decoration_quad(self.rect_shader, self.rect_vbo, self.rect_vao, self._get_orthographic_matrix(), frag_start_x, pen_y + frag_h - 2, frag_w, thickness, frag.color, alpha, (center_x, center_y), rotation)
                    if frag.strikethrough:
                        _draw_decoration_quad(self.rect_shader, self.rect_vbo, self.rect_vao, self._get_orthographic_matrix(), frag_start_x, pen_y + frag_h / 2, frag_w, thickness, frag.color, alpha, (center_x, center_y), rotation)

                vertices = []

                for char in frag.text:
                    glyph = atlas.glyphs.get(char)
                    if glyph is None:
                        continue

                    if glyph.width == 0 or glyph.height == 0:
                        pen_x += glyph.advance
                        continue

                    x0 = pen_x + glyph.bitmap_left
                    y0 = baseline_y - glyph.bitmap_top
                    x1 = x0 + glyph.width
                    y1 = y0 + glyph.height

                    u0 = glyph.uv_x
                    v0 = glyph.uv_y
                    u1 = u0 + glyph.uv_w
                    v1 = v0 + glyph.uv_h

                    vertices.extend([
                        x0, y0, u0, v0,
                        x1, y0, u1, v0,
                        x1, y1, u1, v1,

                        x0, y0, u0, v0,
                        x1, y1, u1, v1,
                        x0, y1, u0, v1,
                    ])

                    pen_x += glyph.advance

                if not vertices:
                    continue

                vertex_data = np.array(vertices, dtype=np.float32)
                needed = vertex_data.nbytes

                if needed > self.text_vbo.size:
                    self.text_vbo = self.context.buffer(reserve=needed * 2)
                    self.text_vao = self.context.vertex_array(
                        self.text_shader,
                        [(self.text_vbo, "2f 2f", "aPos", "aUV")]
                    )

                self.text_vbo.write(vertex_data)
                self.text_vao.render(moderngl.TRIANGLES, vertices=len(vertices) // 4)

        if final_clip:
            self.context.scissor = None

    def _draw_image(self, img_path, x, y, w, h, alpha, clip_rect, rotation):
        if clip_rect:
            cx, cy, cw, ch = clip_rect
            screen_h = self.get_size()[1]
            self.context.scissor = (int(cx), int(screen_h - cy - ch), int(cw), int(ch))

        texture = _texture_cache.get(img_path)
        if texture is None:
            from PIL import Image
            img = Image.open(img_path).convert("RGBA")
            img_data = img.tobytes()
            texture = self.context.texture(img.size, 4, img_data)
            texture.filter = moderngl.LINEAR, moderngl.LINEAR
            _texture_cache[img_path] = texture

        vertices = _get_rect_vertices(x, y, w, h)
        self.image_vbo.write(vertices)

        center_x = x + (w / 2.0)
        center_y = y + (h / 2.0)

        texture.use(location=0)
        self.image_shader['uTexture'].value = 0
        self.image_shader['uAlpha'].value = alpha / 255.0
        self.image_shader['uElementPos'].value = (float(x), float(y))
        self.image_shader['uSize'].value = (float(w), float(h))
        self.image_shader['uRotation'].value = rotation
        self.image_shader['uCenter'].value = (center_x, center_y)
        self.image_shader['projection'].write(self._get_orthographic_matrix())

        self.image_vao.render(moderngl.TRIANGLES)

        if clip_rect:
            self.context.scissor = None

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
        return self.driver._get_size()
    
    def poll_input(self):
        return self.driver._poll_input()
    
    def measure_run(self, font_path, font_size, text):
        from .gl_font import measure_run
        return measure_run(font_path, font_size, text)
    
    def measure_text(self, text_data):
        from .gl_font import measure_text
        return measure_text(text_data)
    
    def _get_orthographic_matrix(self) -> np.ndarray:
        width, height = self.get_size()

        if width == 0 or height == 0:
            return self._orthographic_matrix if self._orthographic_matrix is not None else np.eye(4, dtype=np.float32)

        self.context.viewport = (0, 0, width, height)
        self._orthographic_matrix = np.array([
            2.0 / width, 0.0, 0.0, 0.0,
            0.0, -2.0 / height, 0.0, 0.0,
            0.0, 0.0, -1.0, 0.0,
            -1.0, 1.0, 0.0, 1.0
        ], dtype=np.float32)
        
        return self._orthographic_matrix

# region HELPERS
def _draw_decoration_quad(rect_shader, rect_vbo, rect_vao, projection, x, y, w, h, color, alpha, node_center, rotation):
    """Draws a solid rect (used for underline/strikethrough), rotating the quad's own
    corners around the text node's center so it stays aligned with rotated text."""
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if rotation and rotation != 0.0:
        corners = [_rotate_point_around(cx, cy, node_center[0], node_center[1], rotation) for cx, cy in corners]

    vertices = np.array([
        corners[0][0], corners[0][1],
        corners[1][0], corners[1][1],
        corners[2][0], corners[2][1],

        corners[0][0], corners[0][1],
        corners[2][0], corners[2][1],
        corners[3][0], corners[3][1],
    ], dtype=np.float32)
    rect_vbo.write(vertices)

    r, g, b = color
    rect_shader['inColor'].value = (r / 255.0, g / 255.0, b / 255.0, alpha / 255.0)
    rect_shader['uElementPos'].value = (float(x), float(y))
    rect_shader['uSize'].value = (float(w), float(h))
    rect_shader['uRadius'].value = (0.0, 0.0, 0.0, 0.0)
    rect_shader['uBorderWidth'].value = 0.0
    rect_shader['uBorderColor'].value = (0.0, 0.0, 0.0, 0.0)
    # Rotation is baked into the quad's vertices already, so leave shader rotation off.
    rect_shader['uRotation'].value = 0.0
    rect_shader['uCenter'].value = (0.0, 0.0)
    rect_shader['projection'].write(projection)

    rect_vao.render(moderngl.TRIANGLES)

def _load_program(context, vertex_relative_path: str, fragment_relative_path: str):
    backend_dir = Path(__file__).parent.resolve()

    vertex_path = (backend_dir / vertex_relative_path).resolve()
    fragment_path = (backend_dir / fragment_relative_path).resolve()

    with open(vertex_path, 'r') as f:
        vertex_source = f.read()
        
    with open(fragment_path, 'r') as f:
        fragment_source = f.read()
        
    return context.program(
        vertex_shader=vertex_source,
        fragment_shader=fragment_source
    )

def _get_rect_vertices(x, y, width, height):
    left = x
    right = x + width
    top = y
    bottom = y + height

    return np.array([
        left, top,
        right, top,
        right, bottom,

        left, top,
        right, bottom,
        left, bottom,
    ], dtype=np.float32)

# endregion