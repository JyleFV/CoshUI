from .cui_error import CoshUIError
from .engine import CoshUI
from .nodes import Node, Container
from .types import *
from .backend import CoshBackend
from typing import TypeVar, Generic
import difflib

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

    if isinstance(node, Container):
        if not node.sizing == CoshSizing.FIT:
            return
        
        match node.direction:
            case CoshDirection.ROW:
                node.layout.width = (sum(child.layout.width for child in node.children) + (node.gap * (len(node.children) - 1)))
                node.layout.height = max((child.layout.height for child in node.children), default=0)
            case CoshDirection.COLUMN:
                node.layout.width = max((child.layout.width for child in node.children), default=0)
                node.layout.height = (sum(child.layout.height for child in node.children) + (node.gap * (len(node.children) - 1)))

def layout(node : Node):
    pass

def update(delta : float):
    for tween in CoshUI._active_tweens:
        tween.update(delta)

    CoshUI._active_tweens -= { t for t in CoshUI._active_tweens if t.finished }

def render(node : Node, backend : CoshBackend):
    if isinstance(node, Container): # Temporary so only containers get rendered for now    
        CoshUI._render_stack.append(node.get_render_data())

    for child in node.children:
        render(child, backend)

    backend.flush(CoshUI._render_stack)

def add_font(name : str, path : str):
    if not name or not path:
        raise CoshUIError("Please input a name or a path when adding fonts.")
    
    CoshUI._font_library[name] = path

def set_default_font(name : str):
    try:
        CoshUI._default_font = (name, CoshUI._font_library[name])
    except KeyError:
        raise CoshUIError("That font does not exist in the system. Please do add_font() before this function call with the name and path as arguments.")

def get_node(node_name : str):
    node = CoshUI._node_map.get(node_name)
    if node == None:
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
    for part in parts[:-1]:
        obj = getattr(node, part)
    setattr(obj, parts[-1], value)