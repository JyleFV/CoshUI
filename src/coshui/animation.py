import difflib
import math
from typing import Callable, Optional

from .state import CoshUI
from .cui_error import CoshUIError

# Lerp Functions
def lerp_float(start_value : float | int, end_value, time):
    return start_value + time * (end_value - start_value)

def lerp_tuple(start_tup, end_tup, time):
    return tuple(lerp_float(s, e, time) for s, e in zip(start_tup, end_tup))

# Easing Functions
def ease_linear(t : float):
    return t

def ease_in(t : float):
    return t * t

def ease_out(t : float):
    return 1 - ease_in(1 - t)

def ease_in_out(t : float):
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2 

def ease_out_bounce(t : float):
    if t < (1 / 2.75):
        return 7.5625 * t * t
    elif t < (2 / 2.75):
        t -= (1.5 / 2.75)
        return 7.5625 * t * t + 0.75
    elif t < (2.5 / 2.75):
        t -= (2.25 / 2.75)
        return 7.5625 * t * t + 0.9375
    else:
        t -= (2.625 / 2.75)
        return 7.5625 * t * t + 0.984375

def ease_in_bounce(t : float):
    return 1 - ease_out_bounce(1 - t)

def ease_in_elastic(t: float) -> float:
    c4 = (2 * math.pi) / 3
    if t == 0: return 0
    if t == 1: return 1
    return -(math.pow(2, 10 * t - 10) * math.sin((t * 10 - 10.75) * c4))

def ease_out_elastic(t: float) -> float:
    c4 = (2 * math.pi) / 3
    if t == 0: return 0
    if t == 1: return 1
    return math.pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

EASING_MAP = {
        "linear" : ease_linear,
        "ease_in" : ease_in,
        "ease_out" : ease_out,
        "ease_in_out" : ease_in_out,
        "ease_in_bounce" : ease_in_bounce,
        "ease_out_bounce" : ease_out_bounce,
        "ease_in_elastic" : ease_in_elastic,
        "ease_out_elastic" : ease_out_elastic
    }

# FORMAT: "name_to_be_called_in_animate" : ("property", datatype_in_lerp) 
PROPERTY_MAP = {
        "alpha" : ("alpha", lerp_float),
        "transform_scale" : ("transform_scale", lerp_float),
        "transform_position" : ("transform_position", lerp_tuple),
        "background_color" : ("background_color", lerp_tuple),
        "transform_rotation" : ("transform_rotation", lerp_float)
    }

PROPERTY_TYPE_MAP = {
    lerp_float : (int, float),
    lerp_tuple : tuple
}

class Tween:
    def __init__(self, n_property : str, target_id, end_value, duration : float, easing : callable, on_complete : Optional[Callable] = None):
        self.property = n_property
        self.target_id = target_id

        self.path, self.lerp_fn = PROPERTY_MAP.get(n_property) 

        val = CoshUI.get_state(self.target_id, self.path)
        
        # Should be redundant but it's a good visual check
        if val is None:
            if self.lerp_fn == lerp_tuple:
                val = tuple(0 for _ in end_value) 
            else:
                val = 0.0

        self.start_value = val
        self.end_value = end_value
        self.time = 0
        self.duration = duration
        self.easing = easing
        self.on_complete = on_complete
        self.finished = False

    def update(self, delta):
        if self.finished:
            return
        
        self.time += delta
        raw_t = min(self.time / self.duration, 1.0)
        eased_t = self.easing(raw_t)

        new_value = self.lerp_fn(self.start_value, self.end_value, eased_t)
        CoshUI.set_state(self.target_id, self.path, new_value)

        if raw_t >= 1.0:
            self.finished = True

    def reverse(self):
        self.start_value = CoshUI.get_state(self.target_id, self.path)
        self.end_value, self.start_value = self.start_value, self.end_value
        self.time = 0
        self.finished = False

def animate(n_property : str, target_id : str, end_value, duration : float, easing : str, on_complete : Optional[Callable] = None):
    """
    Animates a node property over time. 
    
    This function creates a `Tween` object and adds it
    to the global `_active_tweens` registry to be updated per frame.

    :param n_property: The property you want to animate (e.g., 'position', 'scale', or 'alpha').
    :param target_id: The id of the node instance the animation is applied to.
    :param end_value: The final target value to reach by the end of the animation.
    :param duration: Animation length in seconds.
    :param easing: The easing curve name. Defaults to 'linear' if not passed.
    :param on_complete: A callable that gets called once the tween is finished.

    .. note ::
        **Best Practice:** Call this inside a callable passed to event fields. 
        **Requirement:** Ensure the target and Node that holds this callable has an `id`. Nodes with no id are not persistent as of pre-v1.0.0 and may cause tweens to fail.
    """

    # TODO: Do more comprehensive checks on each parameter and raise CoshUIErrors for better DX.

    if n_property not in PROPERTY_MAP:
        close_match = difflib.get_close_matches(n_property, PROPERTY_MAP.keys(), n=1)
        raise CoshUIError(f"Unknown property `{n_property}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`? Valid properties are: {list(PROPERTY_MAP.keys())}.")
    
    _, lerp_fn = PROPERTY_MAP[n_property]
    expected_type = PROPERTY_TYPE_MAP.get(lerp_fn)

    if expected_type and not isinstance(end_value, expected_type):
        raise CoshUIError(f"Property `{n_property}` expects `{expected_type}`, got `{type(end_value).__name__}`.")

    existing_tween = next((t for t in CoshUI._active_tweens if t.target_id == target_id and t.property == n_property), None)

    if existing_tween:
        if existing_tween.end_value == end_value:
            return
        
        CoshUI._active_tweens.remove(existing_tween)

    ease_fn = EASING_MAP.get(easing, ease_linear)
    tween = Tween(n_property, target_id, end_value, duration, ease_fn, on_complete)
    CoshUI._active_tweens.add(tween)