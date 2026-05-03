import difflib

from .nodes import Node
from .types import ease_in, ease_in_out, ease_linear, ease_out, lerp_float, lerp_tuple
from .engine import CoshUI
from .utility import get_nested_attr, set_nested_attr
from .cui_error import CoshUIError

EASING_MAP = {
        "linear" : ease_linear,
        "ease_in" : ease_in,
        "ease_out" : ease_out,
        "ease_in_out" : ease_in_out
    }

PROPERTY_MAP = {
        "alpha" : ("style.alpha", lerp_float),
        "scale" : ("style.transform_scale", lerp_float),
        "position" : ("style.transform_position", lerp_tuple),
        "background_color" : ("style.background_color", lerp_tuple),
        "rotation" : ("style.transform_rotation", lerp_float)
    }

PROPERTY_TYPE_MAP = {
    lerp_float : (int, float),
    lerp_tuple : tuple
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
    """
    Animates a node property over time. 
    
    This function creates a `Tween` object and adds it
    to the global `_active_tweens` registry to be updated per frame.

    :param n_property: The property you want to animate (e.g., 'position', 'scale', or 'alpha').
    :param target: The Node instance the animation is applied to.
    :param end_value: The final target value to reach by the end of the animation.
    :param duration: Animation length in seconds.
    :param easing: The easing curve name. Defaults to 'linear' if not passed.

    .. note ::
        **Best Practice:** Call this inside a callable passed to event fields. 
        **Requirement:** Ensure the target has an `id`. Nodes with no id are not persistent as of pre-v1.0.0 and may cause tweens to fail.
    """

    # TODO: Do more comprehensive checks on each parameter and raise CoshUIErrors for better DX.

    if n_property not in PROPERTY_MAP:
        close_match = difflib.get_close_matches(n_property, PROPERTY_MAP.keys(), n=1)
        raise CoshUIError(f"Unknown property `{n_property}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`? Valid properties are: {list(PROPERTY_MAP.keys())}.")
    
    _, lerp_fn = PROPERTY_MAP[n_property]
    expected_type = PROPERTY_TYPE_MAP.get(lerp_fn)

    if expected_type and not isinstance(end_value, expected_type):
        raise CoshUIError(f"Property `{n_property}` expects `{expected_type}`, got `{type(end_value).__name__}`.")

    target_id = target.id

    existing_tween = next((t for t in CoshUI._active_tweens if t.target.id == target_id and t.property == n_property), None)

    if existing_tween:
        if existing_tween.end_value == end_value:
            return
        
        CoshUI._active_tweens.remove(existing_tween)

    ease_fn = EASING_MAP.get(easing, ease_linear)
    tween = Tween(n_property, target, end_value, duration, ease_fn)
    CoshUI._active_tweens.add(tween)