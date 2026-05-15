from __future__ import annotations
from typing import TYPE_CHECKING
import os
import math
from dataclasses import dataclass

from .types import *
from .utility import Ref
from .state import CoshUI
from .cui_error import CoshUIError, warn
from .node_definitions import Element, TextNode, ParentNode
from ._defaults import _button_default_click, _button_default_hover, _button_default_release, _button_default_unhover, _checkbox_default_click

if TYPE_CHECKING:
    from .utility import Ref

# ======================== Parent Nodes ========================

@dataclass
class Container(ParentNode):
    """The base Container Node, simple but the most customizable."""

    direction : CoshDirection = CoshDirection.ROW

    def measure(self):
        if self.sizing == CoshSizing.FILL:
            return

        match self.direction:
            case CoshDirection.ROW:
                if self.width is CoshSizing.AUTO:
                    self.width = (sum(child.width + (child.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL) + (self.gap * (len(self.children) - 1))) + (self.padding * 2)
                if self.height is CoshSizing.AUTO:
                    self.height = max((child.height + (child.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0) + (self.padding * 2)
            case CoshDirection.COLUMN:
                if self.width is CoshSizing.AUTO:
                    self.width = max((child.width + (child.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0) + (self.padding * 2)
                if self.height is CoshSizing.AUTO:
                    self.height = (sum(child.height + (child.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL) + (self.gap * (len(self.children) - 1))) + (self.padding * 2)

@dataclass
class Grid(ParentNode):
    """A "container-like" node but specially designed for containing stacked elements with a predictable amount of elements per row."""
    
    column_count : int = 1

    def measure(self):
        if self.sizing == CoshSizing.FILL:
            return

        rows = math.ceil(len(self.children) / self.column_count)
        max_child_width = max((child.width + (child.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0)
        max_child_height = max((child.height + (child.margin * 2) for child in self.children if child.sizing != CoshSizing.FILL), default=0)

        if self.width is CoshSizing.AUTO:
            self.width = (max_child_width * self.column_count) + (self.gap * (self.column_count - 1)) + (self.padding * 2)
        if self.height is CoshSizing.AUTO:
            self.height = (max_child_height * rows) + (self.gap * (rows - 1)) + (self.padding * 2)

# ======================== Widgets ========================

# NOTE: Conditional UI is partially unsupported. It's possible, just don't forget to explicitly add ids to all UI elements that appear within conditionals.
@dataclass
class Button(TextNode):
    def __post_init__(self):
        super().__post_init__()

        if CoshUI._get_signal(self.id, CoshSignals.HOVER_ENTER):
            _button_default_hover(self.id)
        if CoshUI._get_signal(self.id, CoshSignals.HOVER_EXIT):
            _button_default_unhover(self.id)
        if CoshUI._get_signal(self.id, CoshSignals.CLICKED):
            _button_default_click(self.id)
        if CoshUI._get_signal(self.id, CoshSignals.RELEASED):
            _button_default_release(self.id)

# This is basically nothing since TextNode is just what Label is
@dataclass
class Label(TextNode):
    pass

@dataclass
class Checkbox(Element):
    """ NOTE: Checkboxes don't support background_color animations as background_color is a direct representation of it's functional state """
    checked : bool =  False
    checked_color : tuple | None = None
    unchecked_color : tuple | None = None
    bind : Ref | None = None

    def __post_init__(self):
        if CoshUI._get_signal(self.id, CoshSignals.CLICKED):
            _checkbox_default_click(self.id)

        super().__post_init__()       

        stored_checked = CoshUI.get_state(self.id, "checked")
        if stored_checked is not None:
            self.checked = stored_checked
            if self.bind is not None:
                self.bind.value = self.checked
        else:
            CoshUI.set_state(self.id, "checked", self.checked)

    def get_render_data(self):
        return RenderContext(**self.get_base_render_data())

@dataclass
class Image(Element):
    src : str | None = None
    
    def __post_init__(self):
        super().__post_init__()

        if self.src:
            self.src = os.path.abspath(self.src)
            if not os.path.isfile(self.src):
                raise CoshUIError(f"Image path `{self.src}` does not exist or is not a file.")
        else:
            raise CoshUIError(f"Expected path value in `src` field.")

    def get_render_data(self):
        data = self.get_base_render_data()
        data["image_src"] = self.src
        return RenderContext(**data)

# Literally just a filler datatype
@dataclass
class Box(Element):
    def get_render_data(self):
        return RenderContext(**self.get_base_render_data())

# ======================== Atomic Widgets ========================

# ======================== Composite Widgets ========================

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
            raise CoshUIError("ParentNode `Modal` must have an id.")

        super().__post_init__()

    def measure(self):
        pass

@dataclass
class InputField(TextNode):
    pass

@dataclass
class Dropdown(TextNode):
    pass

@dataclass
class Slider(Element):
    min_value : float = 0.0
    max_value : float = 100.0
    step : float = 1.0
    value : float | None = None
    bind : Ref | None = None
    thumb_size : int | None = None
    thumb_color : tuple | None = None
    track_color : tuple | None = None
    
    def __post_init__(self):
        super().__post_init__()

        value = CoshUI.get_state(self.id, "value")
        if value is None:
            value = self.value if self.value is not None else (self.bind.value if self.bind is not None else self.min_value)
            value = max(self.min_value, min(self.max_value, value))
            CoshUI.set_state(self.id, "value", value)
            if self.bind is not None:
                self.bind.value = float(value)

    def get_render_data(self):
        return None