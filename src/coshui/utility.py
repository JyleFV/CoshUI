from typing import TypeVar, Generic
import difflib
import os

from .cui_error import CoshUIError
from .engine import CoshUI
from .input import CoshInput
from .nodes import Node, Container, Grid
from .widgets import Button
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

def layout(node : Node, x: float = 0.0, y: float = 0.0):
    node.layout.true_position = (x, y)

    if isinstance(node, Container):
        cursor_x = x + node.layout.padding
        cursor_y = y + node.layout.padding

        for child in node.children:
            layout(child, cursor_x, cursor_y)

            match node.direction:
                case CoshDirection.ROW:
                    cursor_x += child.layout.width + node.gap
                case CoshDirection.COLUMN:
                    cursor_y += child.layout.height + node.gap

    if isinstance(node, Grid):
        cursor_x = x + node.layout.padding
        cursor_y = y + node.layout.padding
        
        for i, child in enumerate(node.children):
            layout(child, cursor_x, cursor_y)
            cursor_x += child.layout.width + node.gap
            
            if (i + 1) % node.column_count == 0:  # end of row
                cursor_x = x + node.layout.padding
                cursor_y += child.layout.height + node.gap

def update(delta : float):
    for tween in CoshUI._active_tweens:
        tween.update(delta)

    CoshUI._active_tweens -= { t for t in CoshUI._active_tweens if t.finished }

def render(node : Node, offset_x : float = 0.0, offset_y : float = 0.0, z_offset : int = 0, is_root : bool = False):
    if not is_root:
        data = node.get_render_data()
        if data:
            data = data._replace(
                transform_x=data.transform_x + offset_x,
                transform_y=data.transform_y + offset_y,
                z_index=data.z_index + z_offset
                # TODO: Make children inherit scale from the parent as well.
            )
            CoshUI._render_stack.append(data)

    tx, ty = node.style.transform_position
    for child in node.children:
        render(child, offset_x + tx, offset_y + ty, z_offset + node.z_index)

# TODO: Rework this to "Capture" the node that's active (focused on).
def process_events():
    mx, my = CoshInput.get_mouse_position()

    for data in reversed(CoshUI._render_stack):
        if data.id is None:
            continue

        node = get_node(data.id)
        if node is None:
            continue

        x = data.x + data.transform_x
        y = data.y + data.transform_y
        hovered = point_in_rect(mx, my, x, y, data.width, data.height)
        
        was_hovered = node._was_hovered
        node._was_hovered = hovered

        if hovered and not was_hovered and node.on_hover:
            node.on_hover()
        if not hovered and was_hovered and node.on_unhover:
            node.on_unhover()
        if hovered and CoshInput.get_mouse_just_pressed() and node.on_click:
            node.on_click()
        if hovered and CoshInput.get_mouse_just_released() and node.on_release:
            node.on_release()

# ================ Layouting and Rendering ================

# ================ Fonts ================

def add_font(name : str, path : str):
    if not name or not path:
        raise CoshUIError("Please input a name or a path when adding fonts.")
    
    if not os.path.isfile(path):
        raise CoshUIError(f"Font path `{path}` does not exist or is not a file")
    
    CoshUI._font_library[name] = path

def set_default_font(name : str):
    try:
        CoshUI._default_font = (name, CoshUI._font_library[name])
    except KeyError:
        raise CoshUIError("That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments.") from None

# ================ Fonts ================

# ================ Nodes ================

def get_node(node_name : str):
    node = CoshUI._node_map.get(node_name)
    if node is None:
        close_match = difflib.get_close_matches(node_name, CoshUI._node_map.keys(), n=1)
        raise CoshUIError(f"Node `{node_name}` doesn't exist. Did you mean `{close_match[0] if close_match else ""}`?")
    return node

# ================ Nodes ================

# ================ Styling Classes ================

def add_class(name : str, style : CoshStyling):
    CoshUI._style_class[name] = style

# ================ Styling Classes ================

# ================ Helper Functions ================

def get_nested_attr(node : Node, n_property : str):
    parts = n_property.split('.')
    obj = node
    for part in parts:
        obj = getattr(obj, part)
    return obj

def set_nested_attr(node : Node, n_property : str, value):
    parts = n_property.split('.')
    obj = node
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], value)

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