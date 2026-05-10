from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Callable
import math

from .cui_error import warn, CoshUIError
from .types import CoshLayout, CoshStyling, CoshDirection, CoshSizing, CoshAlign, CoshJustify, CoshPositioning, CoshOverflow, CoshMouseFilter, CoshTextAlign, CoshTextJustify, CoshTextOverflow, RenderContext

@dataclass
class Node(ABC):
    """ This is the top layer of every UI element in the library, it holds all necessary values that all elements need."""

    layout : CoshLayout = field(default_factory=lambda: CoshLayout())
    style : CoshStyling = field(default_factory=lambda: CoshStyling())
    children : list = field(default_factory=list)
    sizing : CoshSizing = CoshSizing.AUTO
    width : float | None = None 
    height : float | None = None
    x : float | None = None
    y : float | None = None
    classes : str | None = None 
    id : str | None = None
    z_index : int = 0
    _was_hovered : bool = False
    mouse_filter : CoshMouseFilter = CoshMouseFilter.STOP
    positioning : CoshPositioning = CoshPositioning.RELATIVE

    def __post_init__(self):
        from .engine import CoshLifecycle
        CoshLifecycle.register_node(self)

        if self.positioning == CoshPositioning.ABSOLUTE and self.sizing == CoshSizing.FILL:
            warn("`sizing=CoshSizing.FILL` has no effect on absolute children. Use explicit `width` and `height` instead.")

        if self.sizing == CoshSizing.FILL:
            if not all(dim is None for dim in (self.width, self.height)):
                warn("`sizing` is set to `CoshSizing.FILL`. Explicit `width` and `height` values will be ignored.")
        else:
            if self.width is not None:
                self.layout.width = self.width
            if self.height is not None:
                self.layout.height = self.height

        # Warning for users who explicitly set x and y but positioning isn't set to ABSOLUTE
        if self.positioning != CoshPositioning.ABSOLUTE and not all(item is None for item in (self.x, self.y)):
            warn("Current `positioning` property is currently set to RELATIVE. `x` and `y` properties will be ignored.")
        
        self.layout.true_position = (self.x if self.x is not None else 0.0, self.y if self.y is not None else 0.0)

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def get_render_data(self) -> RenderContext:
        pass

    def get_base_render_data(self) -> dict:
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return {
            "id" : self.id,
            "x" : x,
            "y" : y,
            "transform_x" : transform_x,
            "transform_y" : transform_y,
            "width" : self.layout.width,
            "height" : self.layout.height,
            "background_color" : self.style.background_color,
            "z_index" : self.z_index,
            "border_radius" : self.style.border_radius,
            "alpha" : self.style.alpha,
            "transform_scale" : self.style.transform_scale,
            "border" : self.style.border,
            "mouse_filter" : self.mouse_filter
        }

@dataclass
class ParentNode(Node):
    """A separate node that still inherits from Node but has custom methods specialized for "container-type" nodes."""
    
    justify : CoshJustify = CoshJustify.START
    align : CoshAlign = CoshAlign.START
    overflow : CoshOverflow = CoshOverflow.VISIBLE
    gap : float = 0.0
    src : str | None = None

    def __enter__(self):
        from .engine import CoshUI
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        from .engine import CoshUI
        CoshUI._stack.pop()

    def get_render_data(self) -> RenderContext:
        data = self.get_base_render_data()
        data["image_src"] = self.src
        return RenderContext(**data)

@dataclass
class Container(ParentNode):
    """The base Container Node, simple but the most customizable."""

    direction : CoshDirection = CoshDirection.ROW

    def measure(self):
        if self.sizing == CoshSizing.FILL:
            return

        match self.direction:
            case CoshDirection.ROW:
                if self.layout.width is CoshSizing.AUTO:
                    self.layout.width = (sum(child.layout.width + (child.layout.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL) + (self.gap * (len(self.children) - 1))) + (self.layout.padding * 2)
                if self.layout.height is CoshSizing.AUTO:
                    self.layout.height = max((child.layout.height + (child.layout.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0) + (self.layout.padding * 2)
            case CoshDirection.COLUMN:
                if self.layout.width is CoshSizing.AUTO:
                    self.layout.width = max((child.layout.width + (child.layout.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0) + (self.layout.padding * 2)
                if self.layout.height is CoshSizing.AUTO:
                    self.layout.height = (sum(child.layout.height + (child.layout.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL) + (self.gap * (len(self.children) - 1))) + (self.layout.padding * 2)

@dataclass
class Grid(ParentNode):
    """A "container-like" node but specially designed for containing stacked elements with a predictable amount of elements per row."""
    
    column_count : int = 1

    def measure(self):
        if self.sizing == CoshSizing.FILL:
            return

        rows = math.ceil(len(self.children) / self.column_count)
        max_child_width = max((child.layout.width + (child.layout.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0)
        max_child_height = max((child.layout.height + (child.layout.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0)

        if self.layout.width is CoshSizing.AUTO:
            self.layout.width = (max_child_width * self.column_count) + (self.gap * (self.column_count - 1)) + (self.layout.padding * 2)
        if self.layout.height is CoshSizing.AUTO:
            self.layout.height = (max_child_height * rows) + (self.gap * (rows - 1)) + (self.layout.padding * 2)

@dataclass
class Modal(ParentNode):
    positioning : CoshPositioning = CoshPositioning.ABSOLUTE
    direction : CoshDirection = CoshDirection.ROW
    header_color : tuple | None = None
    header_border_radius : tuple | None = None
    content_color : tuple | None = None
    content_border_radius : tuple | None = None

    def __post_init__(self):
        if self.id is None:
            raise CoshUIError("Modal must have an id.")

        super().__post_init__()

    def measure(self):
        pass

@dataclass
class Element(Node):
    """Base Element node that widgets inherit from. Mostly useless except for the use of clarity for developers and passing the measure() abstract method."""
    
    sizing : CoshSizing = CoshSizing.AUTO

    def measure(self):
        pass

@dataclass
class TextNode(Element):
    text : str | None = None
    font : str | None = None
    font_size : int | None = None
    text_color : tuple = (255, 255, 255)
    text_align : CoshTextAlign = CoshTextAlign.CENTER
    text_justify : CoshTextJustify = CoshTextJustify.CENTER
    text_overflow : CoshTextOverflow = CoshTextOverflow.VISIBLE

    def measure(self):
        from .engine import CoshUI
        if CoshUI._measure_text is None:
            return
        if self.layout.width is CoshSizing.AUTO or self.layout.height is CoshSizing.AUTO:
            font_path = CoshUI._font_library.get(self.font) if self.font else CoshUI._default_font
            w, h = CoshUI._measure_text(self.text, font_path, self.font_size or 16)
            if self.layout.width is CoshSizing.AUTO:
                self.layout.width = w
            if self.layout.height is CoshSizing.AUTO:
                self.layout.height = h

    def get_render_data(self):
        from .engine import CoshUI
        data = self.get_base_render_data()
        data["text"] = self.text
        data["font"] = CoshUI._font_library.get(self.font) if self.font else CoshUI._default_font
        data["font_size"] = self.font_size
        data["text_color"] = self.text_color
        data["text_align"] = self.text_align
        data["text_justify"] = self.text_justify
        data["text_overflow"] = self.text_overflow
        return RenderContext(**data)