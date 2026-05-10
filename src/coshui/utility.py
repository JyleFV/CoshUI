from typing import TypeVar, Generic
import difflib
import os

from .cui_error import CoshUIError
from .engine import CoshUI
from .input import CoshInput
from .nodes import Node, Container, Grid
from .types import *

T = TypeVar('T')
class Ref(Generic[T]):
    def __init__(self, value : T) -> None:
        self._value : T = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value : T):
        self._value = new_value

# ================ Layout, Updating, Events, and Rendering ================

def measure(node : Node):
    for child in node.children:
        measure(child)
    node.measure()

# TODO: SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY, and STRETCH
# TODO: AUTO and FILL "chicken vs egg" problem
def layout(node : Node, x: float = 0.0, y: float = 0.0):
    node.layout.true_position = (x, y)

    if node.layout.width is CoshSizing.AUTO:
        node.layout.width = 0.0
    if node.layout.height is CoshSizing.AUTO:
        node.layout.height = 0.0

    for child in node.children:
        if child.layout.width is CoshSizing.AUTO:
            child.layout.width = 0.0
        if child.layout.height is CoshSizing.AUTO:
            child.layout.height = 0.0

    if isinstance(node, Container):
        relative_children = [c for c in node.children if c.positioning != CoshPositioning.ABSOLUTE]
        absolute_children = [c for c in node.children if c.positioning == CoshPositioning.ABSOLUTE]

        if node.direction == CoshDirection.ROW:
            total_content_size = sum(c.layout.width + (c.layout.margin * 2) for c in relative_children) + (node.gap * max(0, (len(relative_children)) - 1))
        else:
            total_content_size = sum(c.layout.height + (c.layout.margin * 2) for c in relative_children) + (node.gap * max(0, (len(relative_children)) - 1))

        cursor_x = x + node.layout.padding
        cursor_y = y + node.layout.padding

        if node.direction == CoshDirection.ROW:
            total_gap = node.gap * max(0, (len(relative_children)) - 1)
            available_width = node.layout.width - (node.layout.padding * 2) - total_gap

            fill_widgets = [child for child in relative_children if child.sizing is CoshSizing.FILL]
            static_widgets = [child for child in relative_children if child.sizing is not CoshSizing.FILL]

            for widget in static_widgets:
                available_width -= (widget.layout.width + widget.layout.margin * 2)
            
            if fill_widgets:
                shared_width = max(0, available_width / len(fill_widgets))
                for child in fill_widgets:
                    child.layout.width = shared_width
                    child.layout.height = node.layout.height - (node.layout.padding * 2) - (child.layout.margin * 2)

            total_content_size = sum(c.layout.width + (c.layout.margin * 2) for c in relative_children) + total_gap

            match node.justify:
                case CoshJustify.CENTER:
                    cursor_x = x + (node.layout.width / 2) - (total_content_size / 2)
                case CoshJustify.END:
                    cursor_x = x + node.layout.width - node.layout.padding - total_content_size
        else:
            total_gap = node.gap * max(0, (len(relative_children)) - 1)
            available_height = node.layout.height - (node.layout.padding * 2) - total_gap

            fill_widgets = [child for child in relative_children if child.sizing is CoshSizing.FILL]
            static_widgets = [child for child in relative_children if child.sizing is not CoshSizing.FILL]

            for widget in static_widgets:
                available_height -= (widget.layout.height + widget.layout.margin * 2)
            
            if fill_widgets:
                shared_height = max(0, available_height / len(fill_widgets))
                for child in fill_widgets:
                    child.layout.height = shared_height
                    child.layout.width = node.layout.width - (node.layout.padding * 2) - (child.layout.margin * 2)

            total_content_size = sum(c.layout.height + (c.layout.margin * 2) for c in relative_children) + total_gap

            match node.justify:
                case CoshJustify.CENTER:
                    cursor_y = y + (node.layout.height / 2) - (total_content_size / 2)
                case CoshJustify.END:
                    cursor_y = y + node.layout.height - node.layout.padding - total_content_size

        for child in relative_children:
            if node.direction == CoshDirection.ROW:
                match node.align:
                    case CoshAlign.START:  child_y = y + node.layout.padding
                    case CoshAlign.CENTER: child_y = y + (node.layout.height / 2) - ((child.layout.height + child.layout.margin * 2) / 2)
                    case CoshAlign.END:    child_y = y + node.layout.height - node.layout.padding - (child.layout.height + child.layout.margin * 2)
                
                layout(child, cursor_x + child.layout.margin, child_y + child.layout.margin)
                cursor_x += child.layout.width + (child.layout.margin * 2) + node.gap

            else:
                match node.align:
                    case CoshAlign.START:  child_x = x + node.layout.padding
                    case CoshAlign.CENTER: child_x = x + (node.layout.width / 2) - ((child.layout.width + child.layout.margin * 2) / 2)
                    case CoshAlign.END:    child_x = x + node.layout.width - node.layout.padding - (child.layout.width + child.layout.margin * 2)
                
                layout(child, child_x + child.layout.margin, cursor_y + child.layout.margin)
                cursor_y += child.layout.height + (child.layout.margin * 2) + node.gap
        
        for child in absolute_children:
            if node.direction == CoshDirection.ROW:
                match node.align:
                    case CoshAlign.START:  base_y = y + node.layout.padding
                    case CoshAlign.CENTER: base_y = y + (node.layout.height / 2) - ((child.layout.height + child.layout.margin * 2) / 2)
                    case CoshAlign.END:    base_y = y + node.layout.height - node.layout.padding - (child.layout.height + child.layout.margin * 2)
                    case _:                base_y = y + node.layout.padding
                match node.justify:
                    case CoshJustify.CENTER: base_x = x + (node.layout.width / 2) - ((child.layout.width + child.layout.margin * 2) / 2)
                    case CoshJustify.END:    base_x = x + node.layout.width - node.layout.padding - (child.layout.width + child.layout.margin * 2)
                    case _:                  base_x = x + node.layout.padding
            else:
                match node.align:
                    case CoshAlign.START:  base_x = x + node.layout.padding
                    case CoshAlign.CENTER: base_x = x + (node.layout.width / 2) - ((child.layout.width + child.layout.margin * 2) / 2)
                    case CoshAlign.END:    base_x = x + node.layout.width - node.layout.padding - (child.layout.width + child.layout.margin * 2)
                    case _:                base_x = x + node.layout.padding
                match node.justify:
                    case CoshJustify.CENTER: base_y = y + (node.layout.height / 2) - ((child.layout.height + child.layout.margin * 2) / 2)
                    case CoshJustify.END:    base_y = y + node.layout.height - node.layout.padding - (child.layout.height + child.layout.margin * 2)
                    case _:                  base_y = y + node.layout.padding

            layout(child, base_x + child.layout.true_position[0], base_y + child.layout.true_position[1])

    if isinstance(node, Grid):
        relative_children = [c for c in node.children if c.positioning != CoshPositioning.ABSOLUTE]
        absolute_children = [c for c in node.children if c.positioning == CoshPositioning.ABSOLUTE]

        rows = [relative_children[i:i + node.column_count] for i in range(0, len(relative_children), node.column_count)]
        
        row_heights = [max(child.layout.height + (child.layout.margin * 2) for child in row) for row in rows]
        total_content_height = sum(row_heights) + (node.gap * (len(rows) - 1))

        match node.align:
            case CoshAlign.START:
                current_y = y + node.layout.padding
            case CoshAlign.CENTER:
                current_y = y + (node.layout.height / 2) - (total_content_height / 2)
            case CoshAlign.END:
                current_y = y + node.layout.height - node.layout.padding - total_content_height

        for i, row in enumerate(rows):
            row_width = sum(child.layout.width + (child.layout.margin * 2) for child in row) + (node.gap * (len(row) - 1))
            
            match node.justify:
                case CoshJustify.START:
                    current_x = x + node.layout.padding
                case CoshJustify.CENTER:
                    current_x = x + (node.layout.width / 2) - (row_width / 2)
                case CoshJustify.END:
                    current_x = x + node.layout.width - node.layout.padding - row_width

            for child in row:
                layout(child, current_x + child.layout.margin, current_y + child.layout.margin)
                current_x += child.layout.width + (child.layout.margin * 2) + node.gap

            current_y += row_heights[i] + node.gap

        for child in absolute_children:
            layout(child, x + node.layout.padding + child.layout.true_position[0], 
                          y + node.layout.padding + child.layout.true_position[1])

def update(delta : float):
    for tween in CoshUI._active_tweens:
        tween.update(delta)

    CoshUI._active_tweens -= { t for t in CoshUI._active_tweens if t.finished }

def render(node : Node, offset_x : float = 0.0, offset_y : float = 0.0, z_offset : int = 0, is_root : bool = False, clip_rect=None, accumulated_alpha : int = 255):
    if not is_root:
        data = node.get_render_data()
        if data:
            node_alpha = data.alpha if data.alpha is not None else 255
            blended_alpha = int((accumulated_alpha / 255) * node_alpha)
            data = data._replace(
                transform_x=data.transform_x + offset_x,
                transform_y=data.transform_y + offset_y,
                z_index=data.z_index + z_offset,
                clip_rect=clip_rect,
                alpha=blended_alpha
            )
            CoshUI._render_stack.append(data)
    else:
        blended_alpha = accumulated_alpha

    child_clip = None
    if hasattr(node, 'overflow') and node.overflow == CoshOverflow.HIDDEN:
        child_clip = (node.layout.true_position[0], node.layout.true_position[1], node.layout.width, node.layout.height)

    tx, ty = node.style.transform_position
    child_z_offset = z_offset + node.z_index
    for child in node.children:
        render(child, offset_x + tx, offset_y + ty, child_z_offset, clip_rect=child_clip or clip_rect, accumulated_alpha=blended_alpha)

def process_events():
    mx, my = CoshInput._mouse_position

    if CoshInput.get_mouse_just_released():
        if CoshUI._focused_id:
            CoshUI._emit_signal(CoshUI._focused_id, "released")
            CoshUI._focused_id = None
    
    consumed_hover = False
    consumed_click = False

    for data in reversed(CoshUI._render_stack):
        if data.id is None: 
            continue

        if data.mouse_filter == CoshMouseFilter.IGNORE:
            continue

        was_hovered = CoshUI.get_state(data.id, "_was_hovered", False)

        scale = data.transform_scale
        sw, sh = data.width * scale, data.height * scale
        ox, oy = (data.width - sw) / 2, (data.height - sh) / 2

        tx = data.x + data.transform_x + ox
        ty = data.y + data.transform_y + oy

        if data.clip_rect:
            effective_rect = intersect_rect(
                (tx, ty, sw, sh),
                data.clip_rect
            )
            if effective_rect is None:
                continue
        else:
            effective_rect = (tx, ty, sw, sh)

        hovered = point_in_rect(mx, my, *effective_rect)

        if hovered and not consumed_hover:
            CoshUI.set_state(data.id, "_was_hovered", True)
            CoshUI._emit_signal(data.id, "hovered")
            if not was_hovered:
                CoshUI._emit_signal(data.id, "hover_enter")
            if data.mouse_filter == CoshMouseFilter.STOP:
                consumed_hover = True
        else:
            CoshUI.set_state(data.id, "_was_hovered", False)
            if was_hovered:
                CoshUI._emit_signal(data.id, "hover_exit")

        # Click Logic
        if hovered and not consumed_click:
            if CoshInput.get_mouse_just_pressed():
                CoshUI._emit_signal(data.id, "clicked")
                CoshUI._focused_id = data.id
                if data.mouse_filter == CoshMouseFilter.STOP:
                    consumed_click = True
            if CoshInput.get_mouse_down():
                CoshUI._emit_signal(data.id, "pressed")

# ================ Layouting and Rendering ================

# ================ Fonts ================

def add_font(name : str, path : str):
    if not name or not path:
        raise CoshUIError("Please input a name or a path when adding fonts.")
    
    if not os.path.isfile(path):
        raise CoshUIError(f"Font path `{path}` does not exist or is not a file")
    
    CoshUI._font_library[name] = os.path.abspath(path)

def set_default_font(name : str):
    try:
        path = os.path.abspath(CoshUI._font_library[name])
        CoshUI._default_font = (name, path)
    except KeyError:
        raise CoshUIError("That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments.") from None

# ================ Fonts ================

# ================ Signal Events ================

def get_signal(node_id : str, signal_name : str):
    # TODO: Add this robust check in the future:
    # signals = ["clicked", "released", "hover_enter", "hover_exit", "hovered", "pressed"]
    # if node_id not in CoshUI._signals:
    #     close_match = difflib.get_close_matches(node_id, CoshUI._signals, n=1)
    #     raise CoshUIError(f"`{node_id}` not found in signals registry. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    
    # if signal_name not in signals:
    #     close_match = difflib.get_close_matches(signal_name, signals, n=1)
    #     raise CoshUIError(f"`{signal_name}` is not a valid signal. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")

    return CoshUI._get_signal(node_id, signal_name)

# ================ Signal Events ================

# ================ Styling Classes ================

def add_class(name : str, style : CoshStyling):
    if not isinstance(style, CoshStyling):
        raise CoshUIError("Passed in style is not a CoshStyling object.")
    CoshUI._style_class[name] = style

# ================ Styling Classes ================

# ================ Preload Helpers ================

# NOTE: This currently does practically nothing due to how the architecture is made.
def preload_images(img_paths : str | list):
    """
    Preloads images to the backend to create image textures early.

    :param img_paths: Can be a string with a single value or a list of strings.
    :type img_paths: `str | list`
    :raises CoshUIError: If a path does not exist or is not a file

    .. note :: 
        `preload_images()` converts relative file paths to absolute paths based on the current working directory.

    .. warning::
        Preloading is not yet fully implemented. Images are currently loaded on first render.
        True preloading will be available in a future update.
    """

    if isinstance(img_paths, str):
        img_paths = [img_paths]
    
    for path in img_paths:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise CoshUIError(f"Image path `{abs_path}` doesn't exist or is not a file.")
        
        CoshUI._temp_paths.add(abs_path)

# ================ Preload Helpers ================

# ================ Helper Functions ================

def adjust_brightness_value(rgb, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)

def resolve_border_radius(value : int | float | tuple) -> tuple: 
    match value:
        case int() | float():
            return (value, value, value, value)
        case (a, b, c, d):
            return (a, b, c, d)
        case _:
            raise CoshUIError(f"Invalid border_radius `{value}`. Expected an int/float or a tuple of the 4 corner values (top-left, top-right, bottom-right, bottom-left).")

def point_in_rect(px, py, rx, ry, rw, rh):
    return (rx <= px <= rx + rw and ry <= py <= ry + rh)

def intersect_rect(r1, r2):
    x = max(r1[0], r2[0])
    y = max(r1[1], r2[1])
    w = min(r1[0] + r1[2], r2[0] + r2[2]) - x
    h = min(r1[1] + r1[3], r2[1] + r2[3]) - y
    if w <= 0 or h <= 0:
        return None
    return (x, y, w, h)

def merge_styles(base : CoshStyling, override : CoshStyling) -> CoshStyling:
    return CoshStyling(
        background_color=override.background_color if override.background_color is not None else base.background_color,
        alpha=override.alpha if override.alpha is not None else base.alpha,
        border=override.border if override.border is not None else base.border,
        border_radius=override.border_radius if override.border_radius is not None else base.border_radius,
        transform_position=override.transform_position if override.transform_position is not None else base.transform_position,
        transform_rotation=override.transform_rotation if override.transform_rotation is not None else base.transform_rotation,
        transform_scale=override.transform_scale if override.transform_scale is not None else base.transform_scale
    )