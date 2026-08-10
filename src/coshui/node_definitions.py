from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from .types import *
from .state import CoshUI
from .cui_error import CoshUIError
from .lifecycle import CoshLifecycle
from .utility import create_single_text_data, resolve_font_variant
from ._defaults import ENGINE_DEFAULTS

@dataclass
class Node(ABC):
    """ This is the top layer of every UI element in the library, it holds all necessary values that all elements need."""

    style: CoshStyling = field(default_factory=lambda: CoshStyling())
    children: list = field(default_factory=list)
    width: float | CoshSizing | CoshPercentage | None = None
    height: float | CoshSizing | CoshPercentage | None = None
    margin: float | None = None
    x: float | None = None
    y: float | None = None
    classes: str | None = None 
    id: str | None = None
    z_index: int = 0
    mouse_filter: CoshMouseFilter = CoshMouseFilter.STOP
    positioning: CoshPositioning = CoshPositioning.RELATIVE
    _was_hovered: bool = field(default=False, repr=False)
    _x: float = field(default=0.0, repr=False)
    _y: float = field(default=0.0, repr=False)

    def __post_init__(self):
        CoshLifecycle.register_node(self)

        # Warning for users who explicitly set x and y but positioning isn't set to ABSOLUTE
        if self.positioning is not CoshPositioning.ABSOLUTE and not all(item is None for item in (self.x, self.y)):
            CoshUIError.warn("Current `positioning` property is currently set to RELATIVE. `x` and `y` properties will be ignored.")
        
        self._x = self.x if self.x is not None else 0.0
        self._y = self.y if self.y is not None else 0.0

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def get_render_data(self) -> RenderContext:
        pass

    def valid_property_types(self) -> dict:
        return {
            "width": (int, float, CoshSizing, CoshPercentage, type(None)),
            "height": (int, float, CoshSizing, CoshPercentage, type(None)),
            "margin": (TupleLength(2, 3, 4, element_types=(int, float,)), int, float, type(None)),
            "classes": (str, type(None)),
            "mouse_filter": (CoshMouseFilter,),
            "positioning": (CoshPositioning,),
            "z_index": (int,),
            "id": (str, type(None))
        }
    
    def get_base_render_data(self) -> dict:
        transform_x, transform_y = self.style.transform_position
        return {
            "id": self.id,
            "x": self._x,
            "y": self._y,
            "transform_x": transform_x,
            "transform_y": transform_y,
            "width": self.width,
            "height": self.height,
            "margin": self.margin,
            "background_color": self.style.background_color,
            "z_index": self.z_index,
            "border_radius": self.style.border_radius,
            "alpha": self.style.alpha,
            "transform_rotation": self.style.transform_rotation,
            "transform_scale": self.style.transform_scale,
            "border": self.style.border,
            "mouse_filter": self.mouse_filter
        }

@dataclass
class ParentNode(Node):
    """A separate node that still inherits from Node but has custom methods specialized for "container-type" nodes."""
    
    justify: CoshJustify = CoshJustify.START
    align: CoshAlign = CoshAlign.START
    overflow: CoshOverflow = CoshOverflow.VISIBLE
    padding: float | None = None
    gap: float | None = None
    src: str | None = None

    def __enter__(self):
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        CoshUI._stack.pop()

    def valid_property_types(self):
        base_types = {
            **super().valid_property_types(),
            "justify": (CoshJustify,),
            "align": (CoshAlign,),
            "overflow": (CoshOverflow,),
            "padding": (TupleLength(2, 3, 4, element_types=(int, float,)), int, float, type(None)),
            "gap": (int, float, type(None)),
            "src": (str, type(None))
        }
        return base_types


    def get_render_data(self) -> RenderContext:
        data = self.get_base_render_data()
        data["image_src"] = self.src
        data["padding"] = self.padding
        return RenderContext(**data)

@dataclass
class Element(Node):
    """Base Element node that widgets inherit from. Mostly useless except for the use of clarity for developers and passing the measure() abstract method."""

    def __post_init__(self):
        if self.id is None:
            raise CoshUIError.Main(f"Widget `{self.__class__.__name__}` must have an id.")

        super().__post_init__()

    def measure(self):
        pass

@dataclass
class TextNode(Element):
    text: str | None = None
    font: str | None = None
    font_size: int | None = None
    text_color: tuple = (255, 255, 255)
    text_align: CoshTextAlign = CoshTextAlign.CENTER
    text_justify: CoshTextJustify = CoshTextJustify.CENTER
    text_overflow: CoshTextOverflow = CoshTextOverflow.VISIBLE
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False

    def __post_init__(self):
        super().__post_init__()

        self.font = resolve_font_variant(CoshUI._font_library.get(self.font, None), self.bold, self.italic, self.font)
        self.font_size = self.font_size if self.font_size is not None else ENGINE_DEFAULTS["font_size"]
        self.text_data = create_single_text_data(
            self.text if self.text is not None else "", self.text_align, 
            self.text_justify, self.text_overflow, 
            self.text_color, self.font_size , self.font,
            self.strikethrough, self.underline
        )

    def measure(self):
        if CoshUI._measure_text is None:
            return
        if self.width is CoshSizing.AUTO or self.height is CoshSizing.AUTO:
            w, h = CoshUI._measure_text(self.text_data)
            if self.width is CoshSizing.AUTO:
                self.width = w
            if self.height is CoshSizing.AUTO:
                self.height = h

    def valid_property_types(self):
        base_types = {
            **super().valid_property_types(),
            "text": (str, type(None)),
            "font": (str, type(None)),
            "font_size": (int,),
            "text_color": (TupleLength(3, element_types=(int,)),),
            "text_align": (CoshTextAlign,),
            "text_justify": (CoshTextJustify,),
            "text_overflow": (CoshTextOverflow,),
            "bold": (bool,),
            "italic": (bool,),
            "strikethrough": (bool,),
            "underline": (bool,)
        }
        return base_types

    def get_render_data(self):
        data = self.get_base_render_data()
        data["text_data"] = self.text_data
        return RenderContext(**data)