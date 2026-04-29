from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .types import CoshLayout, CoshStyling, CoshDirection, CoshSizing, RenderRect

@dataclass
class Node(ABC):
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

        # TODO: Add an error for when multiple nodes share the same ID.
        if self.id: # TODO: Do diffs with previous state once that's set up
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
    def __enter__(self):
        from .engine import CoshUI
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        from .engine import CoshUI
        CoshUI._stack.pop()

    @abstractmethod
    def get_render_data(self):
        pass

@dataclass
class Container(ParentNode):
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
        

    def get_render_data(self) -> RenderRect:
        return RenderRect(
            x=self.layout.true_position.x,
            y=self.layout.true_position.y,
            transform_x=self.style.transform_position.x,
            transform_y=self.style.transform_position.y,
            width=self.layout.width,
            height=self.layout.height,
            background_color=self.style.background_color.get_tuple(),
            z_index=self.z_index
        )

@dataclass
class Grid(ParentNode):
    column_count : int = 1
    gap : float = 0.0

    def get_render_data(self) -> RenderRect:
        pass
    
@dataclass
class Element(Node):
    pass

    def measure(self):
        pass

    @abstractmethod
    def get_render_data(self):
        pass
