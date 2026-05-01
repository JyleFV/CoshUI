# Animation-related
from .nodes import Node
from .types import ease_in, ease_in_out, ease_linear, ease_out, lerp_float, lerp_tuple
from .engine import CoshUI
from .utility import get_nested_attr, set_nested_attr

EASING_MAP = {
        "linear" : ease_linear,
        "ease_in" : ease_in,
        "ease_out" : ease_out,
        "ease_in_out" : ease_in_out
    }

PROPERTY_MAP = {
        # Layout
        "true_scale" : ("layout.true_scale", lerp_float),
        "true_position" : ("layout.true_position", lerp_tuple),
        "width" : ("layout.width", lerp_float),
        "height" : ("layout.height", lerp_float),
        
        # Style
        "scale" : ("style.transform_scale", lerp_float),
        "position" : ("style.transform_position", lerp_tuple),
        "background_color" : ("style.background_color", lerp_tuple)
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
        if self.finished:
            return
        
        self.time += delta
        raw_t = min(self.time / self.duration, 1.0)
        eased_t = self.easing(raw_t)

        new_value = self.lerp_fn(self.start_value, self.end_value, eased_t)
        set_nested_attr(self.target, self.path, new_value)

        if raw_t >= 1.0:
            self.finished = True

    def reverse(self):
        self.start_value = get_nested_attr(self.target, self.path)
        self.end_value, self.start_value = self.start_value, self.end_value
        self.time = 0
        self.finished = False

def animate(n_property : str, target : Node, end_value, duration : float, easing : str):
    for t in CoshUI._active_tweens:
        if t.target is target and t.property == n_property and t.end_value == end_value:
            return
    
    CoshUI._active_tweens -= {
        t for t in CoshUI._active_tweens if t.target is target and t.property == n_property
    }
    
    ease_fn = EASING_MAP.get(easing, ease_linear)
    tween = Tween(n_property, target, end_value, duration, ease_fn)
    CoshUI._active_tweens.add(tween)