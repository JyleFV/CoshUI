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

# NOTE: Align is currently the equivalent of CSS's `align-items`
# TODO: Separate Align to `AlignContent` and `AlignItems` to make the library more flexible
def layout(node : Node, x: float = 0.0, y: float = 0.0):
    node.layout.true_position = (x, y)

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
            layout(child, x + node.layout.padding + child.layout.true_position[0], 
                          y + node.layout.padding + child.layout.true_position[1])

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

def render(node : Node, offset_x : float = 0.0, offset_y : float = 0.0, z_offset : int = 0, is_root : bool = False, clip_rect=None):
    if not is_root:
        data = node.get_render_data()
        if data:
            data = data._replace(
                transform_x=data.transform_x + offset_x,
                transform_y=data.transform_y + offset_y,
                z_index=data.z_index + z_offset,
                clip_rect=clip_rect
                # TODO: Make children inherit scale from the parent as well.
            )
            CoshUI._render_stack.append(data)

    child_clip = None
    if hasattr(node, 'overflow') and node.overflow == CoshOverflow.HIDDEN:
        child_clip = (node.layout.true_position[0], node.layout.true_position[1], node.layout.width, node.layout.height)

    tx, ty = node.style.transform_position
    for child in node.children:
        render(child, offset_x + tx, offset_y + ty, z_offset, clip_rect=child_clip or clip_rect)

def process_events():
    mx, my = CoshInput._mouse_position

    if CoshInput.get_mouse_just_released():
        if CoshUI._focused_id:
            actions = CoshUI._action_map.get(CoshUI._focused_id, {})
            if "on_release" in actions:
                actions["on_release"]()
            CoshUI._focused_id = None
    
    consumed_hover = False
    consumed_click = False

    for data in reversed(CoshUI._render_stack):
        if data.id is None: 
            continue

        if data.mouse_filter == CoshMouseFilter.IGNORE:
            continue

        actions = CoshUI._action_map.get(data.id, {})
        was_hovered = CoshUI.get_state(data.id, "_was_hovered", False)

        scale = data.transform_scale
        sw, sh = data.width * scale, data.height * scale
        ox, oy = (data.width - sw) / 2, (data.height - sh) / 2
        
        tx = data.x + data.transform_x + ox
        ty = data.y + data.transform_y + oy
        
        hovered = point_in_rect(mx, my, tx, ty, sw, sh)

        # The property `mouse_filter` works like MOUSE_FILTER_STOP (when True) and MOUSE_FILTER_PASS (when False) in Godot
        # This is due to the consumed_[hover/click] booleans being toggled AFTER the action was done.
        if hovered and not consumed_hover:
            CoshUI.set_state(data.id, "_was_hovered", True)
            if not was_hovered and "on_hover" in actions:
                actions["on_hover"]()
            if data.mouse_filter == CoshMouseFilter.STOP:
                consumed_hover = True
        else:
            CoshUI.set_state(data.id, "_was_hovered", False)
            if was_hovered and "on_unhover" in actions:
                actions["on_unhover"]()

        # Click Logic
        if hovered and not consumed_click and CoshInput.get_mouse_just_pressed():
            if "on_click" in actions:
                actions["on_click"]()
            CoshUI._focused_id = data.id
            if data.mouse_filter == CoshMouseFilter.STOP:
                consumed_click = True

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

# ================ Nodes ================

# def get_node(node_name : str):
#     """
#     Returns the passed in node.
#     """
    
#     node = CoshUI._node_map.get(node_name)
#     if node is None:
#         close_match = difflib.get_close_matches(node_name, CoshUI._node_map.keys(), n=1)
#         raise CoshUIError(f"Node `{node_name}` doesn't exist. Did you mean `{close_match[0] if close_match else ""}`?")
#     return node

# ================ Nodes ================

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

# def get_nested_attr(node : Node, n_property : str):
#     parts = n_property.split('.')
#     obj = node
#     for part in parts:
#         obj = getattr(obj, part)
#     return obj

# def set_nested_attr(node : Node, n_property : str, value):
#     parts = n_property.split('.')
#     obj = node
#     for part in parts[:-1]:
#         obj = getattr(obj, part)
#     setattr(obj, parts[-1], value)

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