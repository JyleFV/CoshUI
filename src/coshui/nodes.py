from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Callable
import math

from .cui_error import warn
from .types import CoshLayout, CoshStyling, CoshDirection, CoshSizing, CoshAlign, CoshJustify, CoshTextAlign, CoshTextJustify, RenderContext

@dataclass
class Node(ABC):
    """ This is the top layer of every UI element in the library, it holds all necessary values that all elements need."""

    layout : CoshLayout = field(default_factory=lambda: CoshLayout())
    style : CoshStyling = field(default_factory=lambda: CoshStyling())
    children : list = field(default_factory=list)
    sizing : CoshSizing = CoshSizing.FIT
    width : float = 0.0 
    height : float = 0.0
    classes : str | None = None 
    id : str | None = None
    z_index : int = 0
    on_hover : Callable | None = None
    on_unhover : Callable | None = None
    on_click : Callable | None = None
    on_release : Callable | None = None
    _was_hovered : bool = False
    mouse_filter : bool = True # Currently a bool, if True, it will capture mouse events, if False, it will ignore mouse events.

    def __post_init__(self):
        from .engine import CoshLifecycle
        CoshLifecycle.register_node(self)

        # These flat parameters take precedence over CoshLayout's width and height for most nodes (ones that don't override __post_init__), which feels weird :/.
        if self.width:
            self.layout.width = self.width
        if self.height:
            self.layout.height = self.height

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def get_render_data(self):
        pass

@dataclass
class ParentNode(Node):
    """A separate node that still inherits from Node but has custom methods specialized for "container-type" nodes."""
    
    justify : CoshJustify = CoshJustify.START
    align : CoshAlign = CoshAlign.START
    gap : float = 0.0

    def __enter__(self):
        from .engine import CoshUI
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        from .engine import CoshUI
        CoshUI._stack.pop()
@dataclass
class Container(ParentNode):
    """The base Container Node, simple but the most customizable."""

    direction : CoshDirection = CoshDirection.ROW

    def measure(self):
        if self.sizing != CoshSizing.FIT:
            return
        
        match self.direction:
            case CoshDirection.ROW:
                self.layout.width = (sum(child.layout.width + (child.layout.margin * 2) for child in self.children) + (self.gap * (len(self.children) - 1))) + (self.layout.padding * 2)
                self.layout.height = max((child.layout.height + (child.layout.margin * 2) for child in self.children), default=0) + (self.layout.padding * 2)
            case CoshDirection.COLUMN:
                self.layout.width = max((child.layout.width + (child.layout.margin * 2) for child in self.children), default=0) + (self.layout.padding * 2)
                self.layout.height = (sum(child.layout.height + (child.layout.margin * 2) for child in self.children) + (self.gap * (len(self.children) - 1))) + (self.layout.padding * 2)
        
    def get_render_data(self) -> RenderContext:
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
            id=self.id,
            x=x,
            y=y,
            transform_x=transform_x,
            transform_y=transform_y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color,
            z_index=self.z_index,
            border_radius=self.style.border_radius,
            alpha=self.style.alpha,
            transform_scale=self.style.transform_scale,
            border=self.style.border,
            mouse_filter=self.mouse_filter
        )

@dataclass
class Grid(ParentNode):
    """A "container-like" node but specially designed for containing stacked elements with a predictable amount of elements per row."""
    
    column_count : int = 1

    def measure(self):
        if self.sizing != CoshSizing.FIT:
            return
        
        rows = math.ceil(len(self.children) / self.column_count)
        max_child_width = max((child.layout.width + (child.layout.margin * 2) for child in self.children), default=0)
        max_child_height = max((child.layout.height + (child.layout.margin * 2) for child in self.children), default=0)
        
        self.layout.width = (max_child_width * self.column_count) + (self.gap * (self.column_count - 1)) + (self.layout.padding * 2)
        self.layout.height = (max_child_height * rows) + (self.gap * (rows - 1)) + (self.layout.padding * 2)

    def get_render_data(self) -> RenderContext:
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
            id=self.id,
            x=x,
            y=y,
            transform_x=transform_x,
            transform_y=transform_y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color,
            z_index=self.z_index,
            border_radius=self.style.border_radius,
            alpha=self.style.alpha,
            transform_scale=self.style.transform_scale,
            border=self.style.border,
            mouse_filter=self.mouse_filter
        )
    
@dataclass
class Element(Node):
    """Base Element node that widgets inherit from. Mostly useless except for the use of clarity for developers and passing the measure() abstract method."""
    
    sizing : CoshSizing = CoshSizing.FIXED

    def measure(self):
        if self.sizing == CoshSizing.FIT:
            warn("`CoshSizing.FIT` is not supported on elements and will be ignored. Use `CoshSizing.FIXED` or `CoshSizing.FILL` instead.")
            

@dataclass
class TextNode(Element):
    text : str | None = None
    font : str | None = None
    font_size : int | None = None
    text_color : tuple = (255, 255, 255)
    text_align : CoshTextAlign = CoshTextAlign.CENTER
    text_justify : CoshTextJustify = CoshTextJustify.CENTER

    def get_render_data(self):
        from .engine import CoshUI
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
            id=self.id,
            x=x,
            y=y,
            transform_x=transform_x,
            transform_y=transform_y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color,
            z_index=self.z_index,
            border_radius=self.style.border_radius,
            alpha=self.style.alpha,
            transform_scale=self.style.transform_scale,
            border=self.style.border,
            text=self.text,
            font=CoshUI._font_library.get(self.font) if self.font else CoshUI._default_font,
            font_size=self.font_size,
            text_color=self.text_color,
            text_align=self.text_align,
            text_justify=self.text_justify,
            mouse_filter=self.mouse_filter
        )
