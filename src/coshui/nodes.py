from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from .types import CoshLayout, CoshStyling
from .engine import CoshUI

@dataclass
class Node(ABC):
    layout : CoshLayout = field(default_factory=lambda: CoshLayout())
    style : CoshStyling = field(default_factory=lambda: CoshStyling())
    children : list = field(default_factory=list)

    def __post_init__(self):
        CoshUI._stack[-1].children.append(self)

@dataclass
class Container(Node):
    gap : float = 0.0

    def __enter__(self):
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        CoshUI._stack.pop()

@dataclass
class Grid(Node):
    column_count : int = 1
    gap : float = 0.0

    def __enter__(self):
        CoshUI._stack.append(self)
        return self

    def __exit__(self, *args):
        CoshUI._stack.pop()

@dataclass
class Element(Node):
    pass
