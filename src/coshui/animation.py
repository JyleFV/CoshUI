import difflib
import math
from typing import Callable, Optional

from .cui_error import CoshUIError

# region Easing and Lerp Functions
# Lerp Functions
def lerp_float(start_value: float | int, end_value, time):
    return start_value + time * (end_value - start_value)

def lerp_tuple(start_tup, end_tup, time):
    return tuple(lerp_float(s, e, time) for s, e in zip(start_tup, end_tup))

# Easing Functions
def ease_linear(t: float):
    return t

def ease_in(t: float):
    return t * t

def ease_out(t: float):
    return 1 - ease_in(1 - t)

def ease_in_out(t: float):
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - math.pow(-2 * t + 2, 2) / 2 

def ease_out_bounce(t: float):
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

def ease_in_bounce(t: float):
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
# endregion

EASING_MAP = {
        "linear": ease_linear,
        "ease_in": ease_in,
        "ease_out": ease_out,
        "ease_in_out": ease_in_out,
        "ease_in_bounce": ease_in_bounce,
        "ease_out_bounce": ease_out_bounce,
        "ease_in_elastic": ease_in_elastic,
        "ease_out_elastic": ease_out_elastic
    }

# FORMAT: "name_to_be_called_in_animate": ("property", datatype_in_lerp) 
PROPERTY_MAP = {
        "alpha": ("alpha", lerp_float),
        "transform_scale": ("transform_scale", lerp_float),
        "transform_position": ("transform_position", lerp_tuple),
        "background_color": ("background_color", lerp_tuple),
        "transform_rotation": ("transform_rotation", lerp_float)
    }

PROPERTY_TYPE_MAP = {
    lerp_float: (int, float),
    lerp_tuple: tuple
}

class Tween:
    def __init__(self, n_property: str, target_id, start_value, end_value, duration: float, easing: Callable, path: str, lerp_fn: Callable):
        self.property = n_property
        self.target_id = target_id
        self.path = path
        self.lerp_fn = lerp_fn

        self.start_value = start_value
        self.end_value = end_value
        self.time = 0
        self.duration = duration
        self.easing = easing
        self._original_start_value = start_value
        self._on_complete = None
        self._finished = False

        self._looping = False
        self._loop_count = None # None = Infinite time
        self._loops_done = 0
        self._ping_pong = False
        self._loop_delay = 0.0
        self._loop_delay_remaining = 0.0
        self._waiting = False

    def _update(self, delta):
        from .state import CoshUI
        if self._finished:
            return

        if self._waiting:
            self._loop_delay_remaining -= delta
            if self._loop_delay_remaining <= 0:
                self._waiting = False
                self.time = 0
                if self._ping_pong:
                    self.start_value, self.end_value = self.end_value, self.start_value
                else:
                    self.start_value = self._original_start_value
            return

        self.time += delta
        raw_t = min(self.time / self.duration, 1.0)
        eased_t = self.easing(raw_t)
        new_value = self.lerp_fn(self.start_value, self.end_value, eased_t)
        CoshUI.set_state(self.target_id, self.path, new_value)

        if raw_t >= 1.0:
            if not self._looping:
                self._finished = True
            else:
                if self._loop_count is not None and self._loops_done + 1 >= self._loop_count:
                    self._finished = True
                else:
                    self._loops_done += 1
                    if self._loop_delay > 0:
                        self._waiting = True
                        self._loop_delay_remaining = self._loop_delay
                    else:
                        self.time = 0
                        if self._ping_pong:
                            self.start_value, self.end_value = self.end_value, self.start_value
                        else:
                            self.start_value = self._original_start_value

    def finished(self, callback: Optional[Callable]):
        if not callable(callback):
            raise CoshUIError.Main(f"Callable: `{callback}` is not a callable.")
        
        if self._on_complete is None:
            self._on_complete = callback
        return self

    def loop(self, count=None, ping_pong=False, delay=0.0):
        if count is not None and (not isinstance(count, int) or count <= 0):
            raise CoshUIError.Main(f"Animation loop `count` parameter must be a positive integer or None, got `{count}`.")
        
        if not isinstance(ping_pong, bool):
            raise CoshUIError.Main(f"Animation loop `ping_pong` parameter must be a bool, got `{type(ping_pong).__name__}`.")
        
        if not isinstance(delay, (int, float)) or delay < 0:
            raise CoshUIError.Main(f"Animation loop `delay` parameter must be a positive number, got `{type(delay).__name__}`.")
        
        self._loop_count = count
        self._ping_pong = ping_pong
        self._loop_delay = delay
        self._looping = True
        return self