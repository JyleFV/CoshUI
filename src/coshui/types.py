from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from typing import NamedTuple
from enum import Enum

from .cui_error import CoshUIError

if TYPE_CHECKING:
    from .text_engine import TextRun

@dataclass
class CoshStyling:
    background_color: tuple | None = None
    alpha: int | None = None
    # gradients: tuple | None = None
    # glow: tuple | None = None
    # drop_shadow: tuple | None = None
    border: tuple | None = None
    border_radius: int | tuple | None = None
    transform_position: tuple | None = None
    transform_rotation: float | None = None
    transform_scale: float | None = None

    def __post_init__(self):
        from .utility import is_valid_border
        # Lets user use a 4 value tuple for background_color or a 3 value tuple with an explicit alpha field or default.
        if self.background_color is not None and len(self.background_color) == 4:
            r, g, b, a = self.background_color
            self.background_color = (r, g, b)
            if self.alpha is None:
                self.alpha = a

        if self.border is not None:
            if is_valid_border(self.border):
                pass # correct format already
            elif isinstance(self.border, tuple) and len(self.border) == 4:
                try:    
                    r, g, b, width = self.border
                    self.border = ((r, g, b), width)
                except TypeError:
                    raise CoshUIError.Main(f"Invalid `border` value `{self.border}`. Expected `((r, g, b), width)` or `(r, g, b, width)` e.g. `((255, 0, 0), 2)` or `(255, 0, 0, 2)`.") from None
            else:
                raise CoshUIError.Main(f"Invalid `border` value `{self.border}`. Expected `((r, g, b), width)` or `(r, g, b, width)` e.g. `((255, 0, 0), 2)` or `(255, 0, 0, 2)`.")

    @staticmethod
    def valid_property_types() -> dict:
        return {
            "background_color": (TupleLength(3, 4, element_types=(int, float)), type(None)),
            "alpha": (int,),
            "border": (tuple, type(None)), # already has a check, so there's no point in doing TupleLength
            "border_radius": (TupleLength(4, element_types=(int, float)), int, float),
            "transform_scale": (int, float),
            "transform_rotation": (int, float),
            "transform_position": (TupleLength(2, element_types=(int, float)),)
        }

class CoshOverflow(Enum):
    HIDDEN = 0
    VISIBLE = 1

class CoshScrollMode(Enum):
    NONE = 0
    X = 1
    Y = 2
    ALL = 3

# Currently a placeholder for CoshScrollMode
# will figure out if other values will be used
@dataclass
class CoshScroll:
    mode: CoshScrollMode = CoshScrollMode.NONE
    scroll_speed: float | int = 20.0
    # overshoot: bool = False
    # scrollbar_visible: bool = False

    # def __post_init__(self):
    #     if self.mode is CoshScrollMode.NONE and (self.overshoot or self.scrollbar_visible):
    #         CoshUIError.warn("The overshoot and scrollbar_visible attributes being set to `True` have no effect when scroll mode is set to `NONE`.")

class CoshMouseButton(Enum):
    LEFT = 0
    RIGHT = 1

class CoshSignals(Enum):
    # Mouse Buttons
    CLICKED = 0
    RELEASED = 1
    PRESSED = 2
    HOVERED = 3
    HOVER_ENTER = 4
    HOVER_EXIT = 5

class CoshTextOverflow(Enum):
    HIDDEN = 0  
    VISIBLE = 1
    WRAP = 2

class CoshPositioning(Enum):
    RELATIVE = 0
    ABSOLUTE = 1

class CoshMouseFilter(Enum):
    STOP = 0
    PASS = 1
    IGNORE = 2

class CoshDirection(Enum):
    ROW = 0
    COLUMN = 1

class CoshTextJustify(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class CoshTextAlign(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2

class CoshJustify(Enum):
    START = 0
    CENTER = 1
    END = 2
    SPACE_BETWEEN = 3
    SPACE_AROUND = 4
    SPACE_EVENLY = 5

class CoshAlign(Enum):
    START = 0
    CENTER = 1
    END = 2
    STRETCH = 3

class CoshSizing(Enum):
    FILL = 0
    AUTO = 1

class CoshMode(Enum):
    NORMAL = 0
    DEBUG = 1

class CoshPercentage:
    def __init__(self, percentage: int):
        self.percentage = percentage / 100

class CoshClamp:
    pass

class CoshMinMax:
    def __init__(self, min_value: int | float, max_value: int | float):
        self.min_value = min_value
        self.max_valuy = max_value

class FourSide(NamedTuple):
    top: float
    right: float
    bottom: float
    left: float

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom

class FourCorner(NamedTuple):
    top_left: float
    top_right: float
    bottom_right: float
    bottom_left: float

class TupleLength:
    """
    A class that helps with type checking tuple properties, it stores tuple lengths
    and the types of the values within the tuples. This should be used as a substitute for 
    the `tuple` data structure in `valid_property_types()` calls.
    """
    def __init__(self, *lengths: int, element_types: tuple[type, ...] | None = None, label: str | None = None):
        self.lengths = lengths
        self.element_types = element_types
        self.label = label or self._build_label()

    def _build_label(self) -> str:
        base = f"a {'/'.join(map(str, self.lengths))}-value tuple"
        if self.element_types:
            type_names = "/".join(t.__name__ for t in self.element_types)
            base += f" of {type_names}"
        return base

    def matches(self, val) -> bool:
        if not isinstance(val, tuple) or len(val) not in self.lengths:
            return False
        if self.element_types is not None:
            for v in val:
                if isinstance(v, bool) and bool not in self.element_types:
                    return False
                if not isinstance(v, self.element_types):
                    return False
        return True

class RenderContext(NamedTuple):
    # Node-specific
    id: str | None = None
    # Layout
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    padding: float = 0.0
    margin: float = 0.0
    # Visual
    z_index: int = 0
    transform_x: float = 0.0
    transform_y: float = 0.0
    background_color: tuple | None = None
    border_radius: int | tuple = 0
    transform_scale: float = 1.0
    transform_rotation: float = 0.0
    border: tuple | None = None
    alpha: int = 0
    # Interaction
    mouse_filter: CoshMouseFilter = CoshMouseFilter.STOP
    scroll_mode: CoshScrollMode = CoshScrollMode.NONE
    scroll_speed: float | int | None = None
    # Text
    text_data: TextData | None = None
    # Image
    image_src: str | None = None
    # Overflow-logic
    clip_rect: tuple | None = None

class RectData:
    pass

class ImageData:
    pass

@dataclass
class TextData:
    letter_spacing: float | None = None
    word_spacing: float | None = None
    line_spacing: float | None = None
    default_font: str | None = None
    default_font_size: int | None = None
    default_color: tuple | None = None
    text_justify: CoshTextJustify = CoshTextJustify.CENTER
    text_align: CoshTextAlign = CoshTextAlign.CENTER
    text_overflow: CoshTextOverflow = CoshTextOverflow.VISIBLE
    text: str | None = None
    raw_text: str | None = None
    runs: list[TextRun] = field(default_factory=list)
    lines: list[LineLayout] = field(default_factory=list)
    _layout_cache_key: tuple | None = None
    
    def cached_state(self):
        return {
            "raw_text": self.raw_text,
            "letter_spacing": self.letter_spacing,
            "word_spacing": self.word_spacing,
            "line_spacing": self.line_spacing,
            "text_align": self.text_align,
            "text_justify": self.text_justify,
            "text_overflow": self.text_overflow,
            "font": self.default_font,
            "font_size": self.default_font_size,
            "color": self.default_color,
        }

@dataclass
class TextFragment:
    text: str
    x: float
    width: float
    color: tuple
    font: str | None
    font_size: int
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False

@dataclass
class LineLayout:
    y: float
    height: float
    fragments: list = field(default_factory=list)

__all__ = ['CoshClamp', 'CoshMinMax', 'CoshScrollMode', 'CoshScroll', 'TupleLength', 'FourSide', 'LineLayout', 'TextFragment', 'TextData', 'RenderContext', 'CoshMode', 'CoshPercentage', 'CoshSignals', 'CoshMouseButton', 'CoshMouseFilter', 'CoshPositioning', 'CoshOverflow', 'CoshStyling', 'CoshAlign', 'CoshJustify', 'CoshTextAlign', 'CoshTextJustify', 'CoshTextOverflow', 'CoshDirection', 'CoshSizing']