from __future__ import annotations
from typing import TYPE_CHECKING
import os
import math
from dataclasses import dataclass

from .types import *
from .user_functions import Ref
from .utility import resolve_font_variant
from .state import CoshUI
from .cui_error import CoshUIError
from .node_definitions import _type_cache, Element, TextNode, ParentNode
from ._defaults import _button_default_click, _button_default_hover, _button_default_release, _button_default_unhover, _checkbox_default_click
from .text_engine import parse_coshml
from ._defaults import ENGINE_DEFAULTS

if TYPE_CHECKING:
    from .utility import Ref

# ======================== Parent Nodes ========================

@dataclass
class Container(ParentNode):
    """
    The base Container Node, simple but the most customizable.
    """
    direction: CoshDirection = CoshDirection.ROW

    def measure(self):
        if not self.children and any(size is CoshSizing.AUTO for size in (self.width, self.height)):
            CoshUIError.warn(f"Container has `AUTO` sizing with no children, setting sizing to `FILL`.")
            if self.width is CoshSizing.AUTO:
                self.width = CoshSizing.FILL
            if self.height is CoshSizing.AUTO:
                self.height = CoshSizing.FILL

        relative_children = [child for child in self.children if child.positioning is not CoshPositioning.ABSOLUTE]
        if not relative_children:
            return

        match self.direction:
            case CoshDirection.ROW:
                children_width = sum(child.width + (child.margin.horizontal) for child in relative_children if child.width is not CoshSizing.FILL and not isinstance(child.width, CoshPercentage))
                total_gap = self.gap * max(0, len(relative_children) - 1)
                auto_width = children_width + total_gap + (self.padding.horizontal)
                auto_height = max([child.height + (child.margin.vertical) for child in relative_children if child.height is not CoshSizing.FILL and not isinstance(child.height, CoshPercentage)], default=0) + (self.padding.vertical)
            case CoshDirection.COLUMN:
                children_height = sum(child.height + (child.margin.vertical) for child in relative_children if child.height is not CoshSizing.FILL and not isinstance(child.height, CoshPercentage))
                total_gap = self.gap * max(0, len(relative_children) - 1)
                auto_height = children_height + total_gap + (self.padding.vertical)
                auto_width = max([child.width + (child.margin.horizontal) for child in relative_children if child.width is not CoshSizing.FILL and not isinstance(child.width, CoshPercentage)], default=0) + (self.padding.horizontal)

        if self.width is CoshSizing.AUTO:
            self.width = auto_width
        if self.height is CoshSizing.AUTO:
            self.height = auto_height

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "direction": (CoshDirection,)
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

@dataclass
class Grid(ParentNode):
    """
    A "container-like" node but specially designed for containing stacked elements with a predictable amount of elements per row.
    """
    column_count: int = 1

    def measure(self):
        if not self.children and any(size is CoshSizing.AUTO for size in (self.width, self.height)):
            CoshUIError.warn(f"Grid has `AUTO` sizing with no children, setting sizing to `FILL`.")
            if self.width is CoshSizing.AUTO:
                self.width = CoshSizing.FILL
            if self.height is CoshSizing.AUTO:
                self.height = CoshSizing.FILL

        relative_children = [child for child in self.children if child.positioning is not CoshPositioning.ABSOLUTE]
        if not relative_children:
            return

        rows = math.ceil(len(relative_children) / self.column_count)

        col_widths = [0.0] * self.column_count
        row_heights = [0.0] * rows

        for index, child in enumerate(relative_children):
            col = index % self.column_count
            row = index // self.column_count

            # If a child has percentage or FILL sizing, treat its intrinsic minimum width contribution as 0.0
            if child.width is CoshSizing.FILL or isinstance(child.width, CoshPercentage):
                child_width = 0.0
            else:
                child_width = child.width + (child.margin.horizontal)
                
            # If a child has percentage or FILL sizing, treat its intrinsic minimum height contribution as 0.0
            if child.height is CoshSizing.FILL or isinstance(child.height, CoshPercentage):
                child_height = 0.0
            else:
                child_height = child.height + (child.margin.vertical)

            col_widths[col] = max(col_widths[col], child_width)
            row_heights[row] = max(row_heights[row], child_height)
        
        min_content_width = sum(col_widths) + (self.gap * max(0, self.column_count - 1)) + (self.padding.horizontal)
        min_content_height = sum(row_heights) + (self.gap * max(0, rows - 1)) + (self.padding.vertical)
        
        if self.width is CoshSizing.AUTO:
            self.width = min_content_width
        if self.height is CoshSizing.AUTO:
            self.height = min_content_height

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "column_count": (int,)
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

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
class RichLabel(TextNode):
    letter_spacing: float | None = None
    line_spacing: float | None = None
    word_spacing: float | None = None

    def __post_init__(self):
        # Skips TextNode straight to Element so we can bypass create_single_text_data()
        Element.__post_init__(self)

        font_name = self.font
        self.font = resolve_font_variant(CoshUI._font_library.get(self.font, None), self.bold, self.italic, self.font)
        self.font_size = self.font_size if self.font_size is not None else ENGINE_DEFAULTS["font_size"]
        
        current = {
            "raw_text": self.text,
            "letter_spacing": self.letter_spacing,
            "word_spacing": self.word_spacing,
            "line_spacing": self.line_spacing,
            "text_align": self.text_align,
            "text_justify": self.text_justify,
            "text_overflow": self.text_overflow,
            "font": self.font,
            "font_size": self.font_size,
            "color": self.text_color,
        }

        text = CoshUI.get_state(self.id, "text_data")
        if text is None or current != text.cached_state():
            parsed_text = parse_coshml(
                self.text if self.text is not None else "", self.text_color, font_name,
                self.font, self.font_size, 
                self.letter_spacing, self.word_spacing, 
                self.line_spacing, self.text_justify, self.text_align, 
                self.text_overflow, self.strikethrough, self.underline,
                self.bold, self.italic
            )
            CoshUI.set_state(self.id, "text_data", parsed_text)
            text = parsed_text

        self.text_data = text
    
    def get_render_data(self):
        data = self.get_base_render_data()
        data["text_data"] = self.text_data

        return RenderContext(**data)

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "letter_spacing": (int, float, type(None)),
                "line_spacing": (int, float, type(None)),
                "word_spacing": (int, float, type(None))
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

@dataclass
class Checkbox(Element):
    """
    Checkboxes don't support background_color animations as background_color is a direct representation of it's functional state
    """
    checked: bool =  False
    checked_color: tuple | None = None
    unchecked_color: tuple | None = None
    bind: Ref | None = None

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

        if self.checked:
            self.style.background_color = self.checked_color
        else:
            self.style.background_color = self.unchecked_color

    def get_render_data(self):
        return RenderContext(**self.get_base_render_data())

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "checked": (bool,),
                "checked_color": (TupleLength(3, element_types=(int,)), type(None)),
                "unchecked_color": (TupleLength(3, element_types=(int,)), type(None)),
                "bind": (Ref, type(None))
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

@dataclass
class Image(Element):
    src: str | None = None
    
    def __post_init__(self):
        super().__post_init__()

        if self.src:
            self.src = os.path.abspath(self.src)
            if not os.path.isfile(self.src):
                raise CoshUIError.Main(f"Image path `{self.src}` does not exist or is not a file.")
        else:
            raise CoshUIError.Main(f"Expected path value in `src` field.")

    def get_render_data(self):
        data = self.get_base_render_data()
        data["image_src"] = self.src
        return RenderContext(**data)

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "src": (str, type(None))
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

# Literally just a filler datatype
@dataclass
class Box(Element):
    def get_render_data(self):
        return RenderContext(**self.get_base_render_data())

# ======================== Atomic Widgets ========================

# ======================== Composite Widgets ========================

@dataclass
class Modal(ParentNode):
    positioning: CoshPositioning = CoshPositioning.ABSOLUTE # overrides Node
    direction: CoshDirection = CoshDirection.ROW # overrides ParentNode
    header_color: tuple | None = None
    header_border_radius: tuple | None = None
    content_color: tuple | None = None
    content_border_radius: tuple | None = None

    def __post_init__(self):
        if self.id is None:
            raise CoshUIError.Main("ParentNode `Modal` must have an id.")

        super().__post_init__()

    def measure(self):
        pass

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "direction": (CoshDirection,), # This class inherits ParentNode, not Container, so this needs to be set.
                "header_color": (TupleLength(3, element_types=(int,)), type(None)),
                "header_border_radius": (TupleLength(4, element_types=(int, float)), int, float, type(None)),
                "content_color": (TupleLength(3, element_types=(int,)), type(None)),
                "content_border_radius": (TupleLength(4, element_types=(int, float)), int, float, type(None))
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

@dataclass
class InputField(TextNode):
    pass

@dataclass
class Dropdown(TextNode):
    item_list: list | None = None
    selector_index: int = 0
    bind: Ref | None = None

    def __post_init__(self):
        if self.item_list is None:
            raise CoshUIError.Main("Widget `Dropdown` must have a valid `item_list`")

        super().__post_init__()

        stored_index = CoshUI.get_state(self.id, "selector_index")
        if stored_index is not None:
            self.selector_index = stored_index
            if self.bind is not None:
                self.bind.value = self.item_list[self.selector_index]
        else:
            CoshUI.set_state(self.id, "selector_index", self.selector_index)
            if self.bind is not None:
                self.bind.value = self.item_list[self.selector_index]

    def get_render_data(self):
        return None

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "item_list": (list,),
                "selector_index": (int,),
                "bind": (Ref, type(None))
            }
            _type_cache[cls] = base_types
            return base_types
        return cache

@dataclass
class Slider(Element):
    min_value: float = 0.0
    max_value: float = 100.0
    step: float = 1.0
    value: float | None = None
    bind: Ref | None = None
    thumb_size: int | None = None
    thumb_color: tuple | None = None
    track_color: tuple | None = None
    
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

    def valid_property_types(self):
        cls = type(self)
        cache = _type_cache.get(cls)
        if cache is None:
            base_types = {
                **super().valid_property_types(),
                "min_value": (int, float),
                "max_value": (int, float),
                "step": (int, float),
                "value": (float,type(None)),
                "bind": (Ref, type(None)),
                "thumb_size": (int, type(None)),
                "thumb_color": (TupleLength(3, element_types=(int,)), type(None)),
                "track_color": (TupleLength(3, element_types=(int,)), type(None))
            }
            _type_cache[cls] = base_types
            return base_types
        return cache