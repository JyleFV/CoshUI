from .cui_error import CoshUIError
from .engine import CoshUI
from .nodes import Node, Container
from .types import *
from .backend import CoshBackend
from typing import TypeVar, Generic
import difflib
import os

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

def measure(node : Node):
    for child in node.children:
        measure(child)
    node.measure()

def layout(node : Node, x: float = 0.0, y: float = 0.0):
    node.layout.true_position.x = x
    node.layout.true_position.y = y

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

def update(delta : float):
    for tween in CoshUI._active_tweens:
        tween.update(delta)

    CoshUI._active_tweens -= { t for t in CoshUI._active_tweens if t.finished }

def render(node : Node, is_root : bool = False):
    if not is_root:
        data = node.get_render_data()
        if data:
            CoshUI._render_stack.append(data)

    for child in node.children:
        render(child)

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

def get_node(node_name : str):
    node = CoshUI._node_map.get(node_name)
    if node is None:
        close_match = difflib.get_close_matches(node_name, CoshUI._node_map.keys(), n=1)
        raise CoshUIError(f"Node `{node_name}` doesn't exist. Did you mean `{close_match[0] if close_match else ""}`?")
    return node

def add_class(name : str, style : CoshStyling):
    CoshUI._style_class[name] = style

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