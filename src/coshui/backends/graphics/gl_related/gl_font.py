import numpy as np

try:
    import freetype
except ImportError:
    freetype = None

# FORMAT: { (font_path, font_size) : GlyphAtlas }
_atlas_cache = {}

ATLAS_SIZE = 512

class GlyphAtlas:
    def __init__(self, texture_data: np.ndarray, glyphs: dict):
        self.texture_data = texture_data  # (ATLAS_SIZE, ATLAS_SIZE) uint8 array
        self.glyphs = glyphs # { char : GlyphInfo }

class GlyphInfo:
    def __init__(self, uv_x, uv_y, uv_w, uv_h, bitmap_left, bitmap_top, advance, width, height):
        self.uv_x = uv_x
        self.uv_y = uv_y
        self.uv_w = uv_w
        self.uv_h = uv_h
        self.bitmap_left = bitmap_left
        self.bitmap_top = bitmap_top
        self.advance = advance
        self.width = width
        self.height = height

def get_atlas(font_path: str, font_size: int) -> GlyphAtlas:
    cache_key = (font_path, font_size)
    if cache_key in _atlas_cache:
        return _atlas_cache[cache_key]

    if freetype is None:
        raise ImportError("freetype-py is not installed. Please install it using `pip install coshui[moderngl]` or `pip install coshui[pyopengl]`, it is required for text rendering.")

    face = freetype.Face(font_path)
    face.set_pixel_sizes(0, font_size)

    atlas_data = np.zeros((ATLAS_SIZE, ATLAS_SIZE), dtype=np.uint8)
    glyphs = {}

    cursor_x = 0
    cursor_y = 0
    row_height = 0

    # Printable ASCII for now
    for char_code in range(32, 128):
        char = chr(char_code)
        face.load_char(char, freetype.FT_LOAD_RENDER)
        bm = face.glyph.bitmap

        bw = bm.width
        bh = bm.rows

        if bw == 0 or bh == 0:
            glyphs[char] = GlyphInfo(0, 0, 0, 0, 0, face.glyph.bitmap_top, face.glyph.advance.x >> 6, 0, 0)
            continue

        # Wrap to next row if needed
        if cursor_x + bw > ATLAS_SIZE:
            cursor_x = 0
            cursor_y += row_height + 1
            row_height = 0

        if cursor_y + bh > ATLAS_SIZE:
            raise RuntimeError("Font atlas too small. Try reducing font size or increasing ATLAS_SIZE.")

        buffer = np.array(bm.buffer, dtype=np.uint8).reshape(bh, bw)
        atlas_data[cursor_y:cursor_y + bh, cursor_x:cursor_x + bw] = buffer

        uv_x = cursor_x / ATLAS_SIZE
        uv_y = cursor_y / ATLAS_SIZE
        uv_w = bw / ATLAS_SIZE
        uv_h = bh / ATLAS_SIZE

        glyphs[char] = GlyphInfo(
            uv_x, uv_y, uv_w, uv_h,
            face.glyph.bitmap_left,
            face.glyph.bitmap_top,
            face.glyph.advance.x >> 6,
            bw, bh
        )
        cursor_x += bw + 1
        row_height = max(row_height, bh)

    atlas = GlyphAtlas(atlas_data, glyphs)
    _atlas_cache[cache_key] = atlas
    return atlas

def measure_text(font_path: str, font_size: int, text: str) -> tuple:
    atlas = get_atlas(font_path, font_size)
    width = sum(atlas.glyphs[c].advance for c in text if c in atlas.glyphs)
    height = font_size
    return (width, height)

def wrap_text(font_path: str, font_size: int, text: str, max_width: float) -> list:
    atlas = get_atlas(font_path, font_size)
    lines = []
    words = text.split(' ')
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        w, _ = measure_text(font_path, font_size, test_line)
        if w <= max_width:
            current_line = test_line
        else:
            if not current_line:
                lines.append(word)
            else:
                lines.append(current_line)
                current_line = word
    if current_line:
        lines.append(current_line)
    return lines