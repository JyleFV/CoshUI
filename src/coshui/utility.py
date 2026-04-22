from .engine import CoshUI
from .nodes import Node
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

def measure():
    pass

def layout():
    pass

def render():
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

# Maybe add these in a different file
def lerp_float():
    pass

def lerp_vector3():
    pass

def ease_linear():
    pass

def ease_in():
    pass

def ease_out():
    pass

def ease_in_out():
    pass

EASING_MAP = {
        "linear" : ease_linear,
        "ease_in" : ease_in,
        "ease_out" : ease_out,
        "ease_in_out" : ease_in_out
    }

PROPERTY_MAP = {
        "scale" : ("style.transform_scale", lerp_float)
    }

class Tween:
    def __init__(self, n_property : str, target, end_value, duration : float, easing : callable):
        self.property = n_property
        self.target = target
        self.start_value = get_nested_attr(target, PROPERTY_MAP.get(n_property))
        self.end_value = end_value
        self.time = 0
        self.duration = duration
        self.easing = easing
        self.finished = False

    def update(self, delta):
        pass

def animate():
    pass
