from dataclasses import dataclass, field
from typing import NamedTuple
from enum import Enum

# TODO: Get rid of Vectors and just use Tuples

@dataclass
class Vector2:
    x : int = 0
    y : int = 0

@dataclass
class FVector2:
    x : float = 0.0
    y : float = 0.0

@dataclass
class Vector3:
    x : int = 0
    y : int = 0
    z : int = 0

    def get_tuple(self):
        return (self.x, self.y, self.z)

@dataclass
class FVector3:
    x : float = 0.0
    y : float = 0.0
    z : float = 0.0

@dataclass
class Vector4:
    x : int = 0
    y : int = 0
    z : int = 0
    w : int = 0

    def get_tuple(self):
        return (self.x, self.y, self.z, self.w) 

@dataclass
class FVector4:
    x : float = 0.0
    y : float = 0.0
    z : float = 0.0
    w : float = 0.0

@dataclass
class CoshLayout:
    true_position : Vector2 = field(default_factory=lambda: Vector2(0, 0))
    true_scale : float = 1.0
    width : float = 0.0
    height : float = 0.0
    padding : float = 0.0
    margin : float = 0.0

@dataclass
class CoshStyling:
    background_color : Vector4 = field(default_factory=lambda: Vector4(0, 0, 0, 0))
    color : Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    border_radius : Vector4 = field(default_factory=lambda: Vector4(0, 0, 0))
    transform_position : Vector2 = field(default_factory=lambda: Vector2(0, 0))
    transform_rotation : float = 0.0
    transform_scale : float = 1.0

class RenderRect(NamedTuple):
    x : float
    y : float
    width : float
    height : float
    background_color : tuple
    z_index : int
    transform_x : float = 0.0
    transform_y : float = 0.0

class CoshDirection(Enum):
    ROW = 0
    COLUMN = 1

class CoshAlignment(Enum):
    TOP = 0
    BOTTOM = 1
    CENTER = 2
    LEFT = 3
    RIGHT = 4

class CoshSizing(Enum):
    FIXED = 0
    FIT = 1
    FILL = 2

def lerp_float(start_value, end_value, time):
    return start_value + time * (end_value - start_value)

def lerp_vector2(start_vec, end_vec, time):
    return Vector2(
        x=lerp_float(start_vec.x, end_vec.x, time),
        y=lerp_float(start_vec.y, end_vec.y, time)
    )

def lerp_vector3(start_vec, end_vec, time):
    return Vector3(
        x=lerp_float(start_vec.x, end_vec.x, time),
        y=lerp_float(start_vec.y, end_vec.y, time),
        z=lerp_float(start_vec.z, end_vec.z, time)
    )

def ease_linear(t : float):
    return t

def ease_in(t : float):
    return t * t

def ease_out(t : float):
    return 1 - (1 - t) * (1 - t)

def ease_in_out(t : float):
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2 

__all__ = ['CoshLayout', 'CoshStyling', 'CoshAlignment', 'CoshDirection', 'CoshSizing','lerp_float', 'lerp_vector2', 'lerp_vector3', 'ease_linear', 'ease_in', 'ease_out', 'ease_in_out', 'Vector2', 'FVector2', 'Vector3', 'FVector3', 'Vector4', 'FVector4']