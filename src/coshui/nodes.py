from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .cui_error import CoshUIError
from .types import CoshLayout, CoshStyling, CoshDirection, CoshSizing, RenderContext


@dataclass
class Node(ABC):
    """ 
    This is the top layer of every UI element in the library, it holds all necessary values that all elements need.
    """

    layout : CoshLayout = field(default_factory=lambda: CoshLayout())
    style : CoshStyling = field(default_factory=lambda: CoshStyling())
    classes : str | None = None 
    id : str = ""
    z_index : int = 0
    children : list = field(default_factory=list)

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
                # existing.stuff = self.stuff
                pass
            CoshUI._node_map[self.id] = self
        
        if self.classes:
            self.style = CoshUI._style_class[self.classes]

@dataclass
class ParentNode(Node):
    """
    A separate node that still inherits from Node but has custom methods specialized for "container-type" nodes.
    """

    def __enter__(self):
        from .engine import CoshUI
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        from .engine import CoshUI
        CoshUI._stack.pop()

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def get_render_data(self):
        pass

@dataclass
class Container(ParentNode):
    """
    The base Container Node, simple but the most customizable.
    """

    sizing : CoshSizing = CoshSizing.FIT
    direction : CoshDirection = CoshDirection.ROW
    gap : float = 0.0

    def measure(self):
        if self.sizing != CoshSizing.FIT:
            return
        
        match self.direction:
            case CoshDirection.ROW:
                self.layout.width = (sum(child.layout.width for child in self.children) + (self.gap * (len(self.children) - 1)))
                self.layout.height = max((child.layout.height for child in self.children), default=0)
            case CoshDirection.COLUMN:
                self.layout.width = max((child.layout.width for child in self.children), default=0)
                self.layout.height = (sum(child.layout.height for child in self.children) + (self.gap * (len(self.children) - 1)))
        

    def get_render_data(self) -> RenderContext:
        x, y = self.layout.true_position
        transform_x, transform_y = self.style.transform_position
        return RenderContext(
            x=x,
            y=y,
            transform_x=transform_x,
            transform_y=transform_y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color,
            z_index=self.z_index,
            border_radius=self.style.border_radius,
            alpha=self.style.alpha
        )

@dataclass
class Grid(ParentNode):
    """
    A "container-like" node but specially designed for containing stacked elements with a predictable amount of elements per row.
    """
    
    column_count : int = 1
    gap : float = 0.0

    def measure(self):
        pass

    def get_render_data(self) -> RenderContext:
        pass
    
@dataclass
class Element(Node):
    """
    Base Element node that widgets inherit from. Mostly useless except for the use of clarity for developers and passing the measure() abstract method.
    """
    
    def measure(self):
        pass
