from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections.abc import Callable
import math

from .cui_error import CoshUIError
from .types import CoshLayout, CoshStyling, CoshDirection, CoshSizing, RenderContext

@dataclass
class Node(ABC):
    """ This is the top layer of every UI element in the library, it holds all necessary values that all elements need."""

    layout : CoshLayout = field(default_factory=lambda: CoshLayout())
    style : CoshStyling = field(default_factory=lambda: CoshStyling())
    classes : str | None = None 
    id : str | None = None
    z_index : int = 0
    children : list = field(default_factory=list)
    on_hover : Callable | None = None
    on_unhover : Callable | None = None
    on_click : Callable | None = None
    on_release : Callable | None = None
    _was_hovered : bool = False
    mouse_filter : bool = False # Currently a bool, if False, it will capture mouse events, if True, it will ignore mouse events.

    def __post_init__(self):
        from .engine import CoshUI
        if CoshUI._stack:
            CoshUI._stack[-1].children.append(self)

        if self.id: 
            if self.id in CoshUI._active_ids:
                raise CoshUIError(f"A node with id `{self.id}` already exists. Node ids must be unique.")

            CoshUI._active_ids.add(self.id)
            existing = CoshUI._node_map.get(self.id)
            if existing is not None and existing is not self:
                self.style = existing.style
                self._was_hovered = existing._was_hovered

            CoshUI._node_map[self.id] = self
        
        if self.classes:
            self.style = CoshUI._style_class[self.classes]

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def get_render_data(self):
        pass

@dataclass
class ParentNode(Node):
    """A separate node that still inherits from Node but has custom methods specialized for "container-type" nodes."""

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

    sizing : CoshSizing = CoshSizing.FIT
    direction : CoshDirection = CoshDirection.ROW
    gap : float = 0.0

    def measure(self):
        if self.sizing != CoshSizing.FIT:
            return
        
        match self.direction:
            case CoshDirection.ROW:
                self.layout.width = (sum(child.layout.width for child in self.children) + (self.gap * (len(self.children) - 1))) + (self.layout.padding * 2)
                self.layout.height = max((child.layout.height for child in self.children), default=0) + (self.layout.padding * 2)
            case CoshDirection.COLUMN:
                self.layout.width = max((child.layout.width for child in self.children), default=0) + (self.layout.padding * 2)
                self.layout.height = (sum(child.layout.height for child in self.children) + (self.gap * (len(self.children) - 1))) + (self.layout.padding * 2)
        
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
            border=self.style.border
        )

@dataclass
class Grid(ParentNode):
    """A "container-like" node but specially designed for containing stacked elements with a predictable amount of elements per row."""
    
    sizing : CoshSizing = CoshSizing.FIT
    column_count : int = 1
    gap : float = 0.0

    def measure(self):
        if self.sizing != CoshSizing.FIT:
            return
        
        rows = math.ceil(len(self.children) / self.column_count)
        max_child_width = max((child.layout.width for child in self.children), default=0)
        max_child_height = max((child.layout.height for child in self.children), default=0)
        
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
            border=self.style.border
        )
    
@dataclass
class Element(Node):
    """Base Element node that widgets inherit from. Mostly useless except for the use of clarity for developers and passing the measure() abstract method."""
    
    def measure(self):
        pass
