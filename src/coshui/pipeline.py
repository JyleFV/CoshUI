from .state import CoshUI
from .input import CoshInput
from .node_definitions import Node
from .widgets import Container, Grid
from .utility import intersect_rect, point_in_rect
from ._defaults import ENGINE_DEFAULTS
from .types import *

def measure(node : Node):
    for child in node.children:
        measure(child)
    node.measure()

# TODO: SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY, and STRETCH
# TODO: AUTO and FILL "chicken vs egg" problem
def layout(node : Node, x: float = 0.0, y: float = 0.0):
    node._x = x
    node._y = y

    if node.width is CoshSizing.AUTO:
        node.width = 0.0
    if node.height is CoshSizing.AUTO:
        node.height = 0.0

    for child in node.children:
        if child.width is CoshSizing.AUTO:
            child.width = 0.0
        if child.height is CoshSizing.AUTO:
            child.height = 0.0

    if isinstance(node, Container):
        relative_children = [c for c in node.children if c.positioning != CoshPositioning.ABSOLUTE]
        absolute_children = [c for c in node.children if c.positioning == CoshPositioning.ABSOLUTE]

        if node.direction == CoshDirection.ROW:
            total_content_size = sum(c.width + (c.margin * 2) for c in relative_children) + (node.gap * max(0, (len(relative_children)) - 1))
        else:
            total_content_size = sum(c.height + (c.margin * 2) for c in relative_children) + (node.gap * max(0, (len(relative_children)) - 1))

        cursor_x = x + node.padding
        cursor_y = y + node.padding

        if node.direction == CoshDirection.ROW:
            total_gap = node.gap * max(0, (len(relative_children)) - 1)
            available_width = node.width - (node.padding * 2) - total_gap

            fill_widgets = [child for child in relative_children if child.sizing is CoshSizing.FILL]
            static_widgets = [child for child in relative_children if child.sizing is not CoshSizing.FILL]

            for widget in static_widgets:
                available_width -= (widget.width + widget.margin * 2)
            
            if fill_widgets:
                shared_width = max(0, available_width / len(fill_widgets))
                for child in fill_widgets:
                    child.width = shared_width
                    child.height = node.height - (node.padding * 2) - (child.margin * 2)

            total_content_size = sum(c.width + (c.margin * 2) for c in relative_children) + total_gap

            match node.justify:
                case CoshJustify.CENTER:
                    cursor_x = x + (node.width / 2) - (total_content_size / 2)
                case CoshJustify.END:
                    cursor_x = x + node.width - node.padding - total_content_size
        else:
            total_gap = node.gap * max(0, (len(relative_children)) - 1)
            available_height = node.height - (node.padding * 2) - total_gap

            fill_widgets = [child for child in relative_children if child.sizing is CoshSizing.FILL]
            static_widgets = [child for child in relative_children if child.sizing is not CoshSizing.FILL]

            for widget in static_widgets:
                available_height -= (widget.height + widget.margin * 2)
            
            if fill_widgets:
                shared_height = max(0, available_height / len(fill_widgets))
                for child in fill_widgets:
                    child.height = shared_height
                    child.width = node.width - (node.padding * 2) - (child.margin * 2)

            total_content_size = sum(c.height + (c.margin * 2) for c in relative_children) + total_gap

            match node.justify:
                case CoshJustify.CENTER:
                    cursor_y = y + (node.height / 2) - (total_content_size / 2)
                case CoshJustify.END:
                    cursor_y = y + node.height - node.padding - total_content_size

        for child in relative_children:
            if node.direction == CoshDirection.ROW:
                match node.align:
                    case CoshAlign.START:  child_y = y + node.padding
                    case CoshAlign.CENTER: child_y = y + (node.height / 2) - ((child.height + child.margin * 2) / 2)
                    case CoshAlign.END:    child_y = y + node.height - node.padding - (child.height + child.margin * 2)
                
                layout(child, cursor_x + child.margin, child_y + child.margin)
                cursor_x += child.width + (child.margin * 2) + node.gap

            else:
                match node.align:
                    case CoshAlign.START:  child_x = x + node.padding
                    case CoshAlign.CENTER: child_x = x + (node.width / 2) - ((child.width + child.margin * 2) / 2)
                    case CoshAlign.END:    child_x = x + node.width - node.padding - (child.width + child.margin * 2)
                
                layout(child, child_x + child.margin, cursor_y + child.margin)
                cursor_y += child.height + (child.margin * 2) + node.gap
        
        for child in absolute_children:
            if node.direction == CoshDirection.ROW:
                match node.align:
                    case CoshAlign.START:  base_y = y + node.padding
                    case CoshAlign.CENTER: base_y = y + (node.height / 2) - ((child.height + child.margin * 2) / 2)
                    case CoshAlign.END:    base_y = y + node.height - node.padding - (child.height + child.margin * 2)
                    case _:                base_y = y + node.padding
                match node.justify:
                    case CoshJustify.CENTER: base_x = x + (node.width / 2) - ((child.width + child.margin * 2) / 2)
                    case CoshJustify.END:    base_x = x + node.width - node.padding - (child.width + child.margin * 2)
                    case _:                  base_x = x + node.padding
            else:
                match node.align:
                    case CoshAlign.START:  base_x = x + node.padding
                    case CoshAlign.CENTER: base_x = x + (node.width / 2) - ((child.width + child.margin * 2) / 2)
                    case CoshAlign.END:    base_x = x + node.width - node.padding - (child.width + child.margin * 2)
                    case _:                base_x = x + node.padding
                match node.justify:
                    case CoshJustify.CENTER: base_y = y + (node.height / 2) - ((child.height + child.margin * 2) / 2)
                    case CoshJustify.END:    base_y = y + node.height - node.padding - (child.height + child.margin * 2)
                    case _:                  base_y = y + node.padding

            layout(child, base_x + child._x, base_y + child._y)

    if isinstance(node, Grid):
        relative_children = [c for c in node.children if c.positioning != CoshPositioning.ABSOLUTE]
        absolute_children = [c for c in node.children if c.positioning == CoshPositioning.ABSOLUTE]

        rows = [relative_children[i:i + node.column_count] for i in range(0, len(relative_children), node.column_count)]
        
        row_heights = [max(child.height + (child.margin * 2) for child in row) for row in rows]
        total_content_height = sum(row_heights) + (node.gap * (len(rows) - 1))

        match node.align:
            case CoshAlign.START:
                current_y = y + node.padding
            case CoshAlign.CENTER:
                current_y = y + (node.height / 2) - (total_content_height / 2)
            case CoshAlign.END:
                current_y = y + node.height - node.padding - total_content_height

        for i, row in enumerate(rows):
            row_width = sum(child.width + (child.margin * 2) for child in row) + (node.gap * (len(row) - 1))
            
            match node.justify:
                case CoshJustify.START:
                    current_x = x + node.padding
                case CoshJustify.CENTER:
                    current_x = x + (node.width / 2) - (row_width / 2)
                case CoshJustify.END:
                    current_x = x + node.width - node.padding - row_width

            for child in row:
                layout(child, current_x + child.margin, current_y + child.margin)
                current_x += child.width + (child.margin * 2) + node.gap

            current_y += row_heights[i] + node.gap

        for child in absolute_children:
            layout(child, x + node.padding + child._x, 
                          y + node.padding + child._y)

def update(delta : float):
    for tween in CoshUI._active_tweens:
        tween.update(delta)

    CoshUI._active_tweens -= { t for t in CoshUI._active_tweens if t.finished }

def render(node : Node, offset_x : float = 0.0, offset_y : float = 0.0, z_offset : int = 0, is_root : bool = False, clip_rect=None, accumulated_alpha : int = 255):
    if not is_root:
        data = node.get_render_data()
        if data:
            node_alpha = data.alpha if data.alpha is not None else 255
            blended_alpha = int((accumulated_alpha / 255) * node_alpha)
            data = data._replace(
                transform_x=data.transform_x + offset_x,
                transform_y=data.transform_y + offset_y,
                z_index=data.z_index + z_offset,
                clip_rect=clip_rect,
                alpha=blended_alpha
            )
            CoshUI._render_stack.append(data)
    else:
        blended_alpha = accumulated_alpha

    child_clip = None
    if hasattr(node, 'overflow') and node.overflow == CoshOverflow.HIDDEN:
        child_clip = (node._x, node._y, node.width, node.height)

    tx, ty = node.style.transform_position
    child_z_offset = z_offset + node.z_index
    for child in node.children:
        render(child, offset_x + tx, offset_y + ty, child_z_offset, clip_rect=child_clip or clip_rect, accumulated_alpha=blended_alpha)

def process_events():
    mx, my = CoshInput._mouse_position

    if CoshInput.get_mouse_just_released():
        if CoshUI._focused_id:
            CoshUI._emit_signal(CoshUI._focused_id, CoshSignals.RELEASED)
            CoshUI._focused_id = None
    
    consumed_hover = False
    consumed_click = False

    for data in reversed(CoshUI._render_stack):
        if data.id is None: 
            continue

        if data.mouse_filter == CoshMouseFilter.IGNORE:
            continue

        was_hovered = CoshUI.get_state(data.id, "_was_hovered", False)

        scale = data.transform_scale
        sw, sh = data.width * scale, data.height * scale
        ox, oy = (data.width - sw) / 2, (data.height - sh) / 2

        tx = data.x + data.transform_x + ox
        ty = data.y + data.transform_y + oy

        if data.clip_rect:
            effective_rect = intersect_rect(
                (tx, ty, sw, sh),
                data.clip_rect
            )
            if effective_rect is None:
                continue
        else:
            effective_rect = (tx, ty, sw, sh)

        hovered = point_in_rect(mx, my, *effective_rect)

        if hovered and not consumed_hover:
            CoshUI.set_state(data.id, "_was_hovered", True)
            CoshUI._emit_signal(data.id, CoshSignals.HOVERED)
            if not was_hovered:
                CoshUI._emit_signal(data.id, CoshSignals.HOVER_ENTER)
            if data.mouse_filter == CoshMouseFilter.STOP:
                consumed_hover = True
        else:
            CoshUI.set_state(data.id, "_was_hovered", False)
            if was_hovered:
                CoshUI._emit_signal(data.id, CoshSignals.HOVER_EXIT)

        # Click Logic
        if hovered and not consumed_click:
            if CoshInput.get_mouse_just_pressed():
                CoshUI._emit_signal(data.id, CoshSignals.CLICKED)
                CoshUI._focused_id = data.id
                if data.mouse_filter == CoshMouseFilter.STOP:
                    consumed_click = True
            if CoshInput.get_mouse_down():
                CoshUI._emit_signal(data.id, CoshSignals.PRESSED)

def finalize_defaults(node):
    targets = [node, node.style, node]
    
    for key, fallback in ENGINE_DEFAULTS.items():
        for target in targets:
            # We only apply the fallback if the attribute exists AND is None
            if hasattr(target, key) and getattr(target, key) is None:
                setattr(target, key, fallback)

    if node.id:
        if node.id not in CoshUI._state_storage:
            CoshUI._state_storage[node.id] = {}

        CoshUI._state_storage[node.id].update({
            "background_color": node.style.background_color,
            "alpha": node.style.alpha,
            "transform_position": node.style.transform_position,
            "transform_scale": node.style.transform_scale,
            "transform_rotation": node.style.transform_rotation,
            "_was_hovered": node._was_hovered
        })

    for child in node.children:
        finalize_defaults(child)