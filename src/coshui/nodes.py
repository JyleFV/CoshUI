from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .types import CoshLayout, CoshStyling

@dataclass
class Node(ABC):
    layout : CoshLayout = field(default_factory=lambda: CoshLayout())
    style : CoshStyling = field(default_factory=lambda: CoshStyling())
    id : str = ""
    children : list = field(default_factory=list)

    def __post_init__(self):
        from .engine import CoshUI
        CoshUI._stack[-1].children.append(self)

        if self.id:
            CoshUI._node_map[self.id] = self

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
    gap : float = 0.0

@dataclass
class Grid(ParentNode):
    column_count : int = 1
    gap : float = 0.0

@dataclass
class Element(Node):
    pass
