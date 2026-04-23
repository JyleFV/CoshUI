from .engine import CoshUI
from .nodes import Node
from .types import *
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

def render(node : Node, backend : CoshBackend):
    pass

def get_node(node_name : str):
    node = CoshUI._node_map.get(node_name)
    if node == None:
        close_match = difflib.get_close_matches(node_name, CoshUI._node_map.keys(), n=1)
        raise Exception(f"Node {node_name} doesn't exist. Did you mean {close_match[-1] if close_match else None}?")
    return node

def get_nested_attr(node : Node, n_property : str):
    parts = n_property.split('.')
    for part in parts:
        obj = getattr(node, part)
    return obj

def set_nested_attr(node : Node, n_property : str, value):
    parts = n_property.split('.')
    for part in parts[:-1]:
        obj = getattr(node, part)
    setattr(obj, parts[-1], value)

# Animation-related
EASING_MAP = {
        "linear" : ease_linear,
        "ease_in" : ease_in,
        "ease_out" : ease_out,
        "ease_in_out" : ease_in_out
    }

PROPERTY_MAP = {
        "true_scale" : ("layout.true_scale", lerp_float)
        "scale" : ("style.transform_scale", lerp_float),
        "background_color" : ("style.background_color", lerp_vector3)
    }

class Tween:
    def __init__(self, n_property : str, target, end_value, duration : float, easing : callable):
        self.property = n_property
        self.target = target

        self.path, self.lerp_fn = PROPERTY_MAP.get(n_property) 

        self.start_value = get_nested_attr(target, self.path)
        self.end_value = end_value
        self.time = 0
        self.duration = duration
        self.easing = easing
        self.finished = False

    def update(self, delta):
        if self.finsihed:
            return
        
        self.time += delta
        raw_t = min(self.time / self.duration, 1.0)
        eased_t = self.easing(raw_t)

        new_value = self.lerp_fn(self.start_value, self.end_value, eased_t)
        set_nested_attr(self.target, self.path, new_value)

        if raw_t >= 1.0:
            self.finished = True

def animate(n_property : str, target : Node, end_value, duration : float, easing : str):
    ease_fn = EASING_MAP.get(easing, ease_linear)
    tween = Tween(n_property, target, end_value, duration, ease_fn)
    CoshUI._active_tweens.add(tween)