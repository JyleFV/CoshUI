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

def layout(node: Node, x: float = 0.0, y: float = 0.0):
    node._x = x
    node._y = y

    if isinstance(node, Container):
        relative_children = [child for child in node.children if child.positioning is not CoshPositioning.ABSOLUTE]
        absolute_children = [child for child in node.children if child.positioning is CoshPositioning.ABSOLUTE]

        cursor_x = x + node.padding
        cursor_y = y + node.padding

        if node.direction is CoshDirection.ROW:
            total_gap = node.gap * max(0, len(relative_children) - 1)
            distributed_gap = node.gap # Default Fallback
            
            available_width = node.width - (node.padding * 2) - total_gap
            fill_widgets = [child for child in relative_children if child.width is CoshSizing.FILL]
            static_widgets = [child for child in relative_children if child.width is not CoshSizing.FILL]

            for widget in static_widgets:
                available_width -= (widget.width + widget.margin * 2)
            
            if fill_widgets:
                shared_width = max(0, available_width / len(fill_widgets))
                for child in fill_widgets:
                    child.width = shared_width

            for child in relative_children:
                if child.height is CoshSizing.FILL:
                    child.height = node.height - (node.padding * 2) - (child.margin * 2)

            raw_inner_width = node.width - (node.padding * 2)
            total_widgets_width = sum(child.width + (child.margin * 2) for child in relative_children)
            leftover_space = raw_inner_width - total_widgets_width

            total_content_size = total_widgets_width + total_gap

            match node.justify:
                case CoshJustify.CENTER:
                    cursor_x = x + (node.width / 2) - (total_content_size / 2)
                case CoshJustify.END:
                    cursor_x = x + node.width - node.padding - total_content_size
                case CoshJustify.SPACE_BETWEEN:
                    if len(relative_children) > 1:
                        distributed_gap = leftover_space / (len(relative_children) - 1)
                        cursor_x = x + node.padding
                    else:
                        cursor_x = x + (node.width / 2) - (total_widgets_width / 2)
                case CoshJustify.SPACE_AROUND:
                    if relative_children:
                        half_gap = leftover_space / (len(relative_children) * 2)
                        cursor_x = x + node.padding + half_gap
                        distributed_gap = half_gap * 2
                case CoshJustify.SPACE_EVENLY:
                    if relative_children:
                        distributed_gap = leftover_space / (len(relative_children) + 1)
                        cursor_x = x + node.padding + distributed_gap

        else:
            total_gap = node.gap * max(0, len(relative_children) - 1)
            distributed_gap = node.gap # Default Fallback

            available_height = node.height - (node.padding * 2) - total_gap
            fill_widgets = [child for child in relative_children if child.height is CoshSizing.FILL]
            static_widgets = [child for child in relative_children if child.height is not CoshSizing.FILL]

            for widget in static_widgets:
                available_height -= (widget.height + widget.margin * 2)
            
            if fill_widgets:
                shared_height = max(0, available_height / len(fill_widgets))
                for child in fill_widgets:
                    child.height = shared_height

            for child in relative_children:
                if child.width is CoshSizing.FILL:
                    child.width = node.width - (node.padding * 2) - (child.margin * 2)

            raw_inner_height = node.height - (node.padding * 2)
            total_widgets_height = sum(child.height + (child.margin * 2) for child in relative_children)
            leftover_space = raw_inner_height - total_widgets_height

            total_content_size = sum(child.height + (child.margin * 2) for child in relative_children) + total_gap

            match node.justify:
                case CoshJustify.CENTER:
                    cursor_y = y + (node.height / 2) - (total_content_size / 2)
                case CoshJustify.END:
                    cursor_y = y + node.height - node.padding - total_content_size
                case CoshJustify.SPACE_BETWEEN:
                    if len(relative_children) > 1:
                        distributed_gap = leftover_space / (len(relative_children) - 1)
                        cursor_y = y + node.padding
                    else:
                        cursor_y = y + (node.width / 2) - (total_widgets_width / 2)
                case CoshJustify.SPACE_AROUND:
                    if relative_children:
                        half_gap = leftover_space / (len(relative_children) * 2)
                        cursor_y = y + node.padding + half_gap
                        distributed_gap = half_gap * 2
                case CoshJustify.SPACE_EVENLY:
                    if relative_children:
                        distributed_gap = leftover_space / (len(relative_children) + 1)
                        cursor_y = y + node.padding + distributed_gap

        for child in relative_children:
            if node.direction is CoshDirection.ROW:
                match node.align:
                    case CoshAlign.START:  child_y = y + node.padding
                    case CoshAlign.CENTER: child_y = y + (node.height / 2) - ((child.height + child.margin * 2) / 2)
                    case CoshAlign.END:    child_y = y + node.height - node.padding - (child.height + child.margin * 2)
                
                layout(child, cursor_x + child.margin, child_y + child.margin)
                cursor_x += child.width + (child.margin * 2) + distributed_gap
            else:
                match node.align:
                    case CoshAlign.START:  child_x = x + node.padding
                    case CoshAlign.CENTER: child_x = x + (node.width / 2) - ((child.width + child.margin * 2) / 2)
                    case CoshAlign.END:    child_x = x + node.width - node.padding - (child.width + child.margin * 2)
                
                layout(child, child_x + child.margin, cursor_y + child.margin)
                cursor_y += child.height + (child.margin * 2) + distributed_gap

        for child in absolute_children:
            if node.direction is CoshDirection.ROW:
                match node.align:
                    case CoshAlign.START:  base_y = y + node.padding
                    case CoshAlign.CENTER: base_y = y + (node.height / 2) - ((child.height + child.margin * 2) / 2)
                    case CoshAlign.END:    base_y = y + node.height - node.padding - (child.height + child.margin * 2)
                    case _:                base_y = y + node.padding
                match node.justify:
                    case CoshJustify.START:  base_x = x + node.padding
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
                    case CoshJustify.START:  base_y = y + node.padding
                    case CoshJustify.CENTER: base_y = y + (node.height / 2) - ((child.height + child.margin * 2) / 2)
                    case CoshJustify.END:    base_y = y + node.height - node.padding - (child.height + child.margin * 2)
                    case _:                  base_y = y + node.padding

            layout(child, base_x + child._x, base_y + child._y)

    if isinstance(node, Grid):
        relative_children = [child for child in node.children if child.positioning is not CoshPositioning.ABSOLUTE]
        absolute_children = [child for child in node.children if child.positioning is CoshPositioning.ABSOLUTE]

        if relative_children:
            # 1. Chunk into rows
            rows = [relative_children[i:i + node.column_count] for i in range(0, len(relative_children), node.column_count)]
            total_rows = len(rows)

            # 2. Pre-calculate grid track sizes from the parent's fixed dimensions
            total_col_gaps = node.gap * max(0, node.column_count - 1)
            total_row_gaps = node.gap * max(0, total_rows - 1)
            
            available_width = node.width - (node.padding * 2) - total_col_gaps
            available_height = node.height - (node.padding * 2) - total_row_gaps

            # This calculates how large each grid cell slot inherently is
            uniform_cell_width = max(0.0, available_width / node.column_count)
            uniform_cell_height = max(0.0, available_height / total_rows)

            column_widths = [0.0] * node.column_count
            row_heights = [0.0] * total_rows

            # 3. Establish track sizes (Respect child's hardcoded sizes if they exceed the uniform cell size)
            for row_index, row in enumerate(rows):
                for column_index, child in enumerate(row):
                    # If child is FILL (or converted to FILL), its intrinsic size contribution is 0,
                    # but it will be safely caught by the uniform cell fallback size.
                    child_width = (child.width + child.margin * 2) if child.width is not CoshSizing.FILL else 0.0
                    child_height = (child.height + child.margin * 2) if child.height is not CoshSizing.FILL else 0.0
                    
                    # The track must be at least as big as the uniform cell slot allocation
                    column_widths[column_index] = max(column_widths[column_index], child_width, uniform_cell_width)
                    row_heights[row_index] = max(row_heights[row_index], child_height, uniform_cell_height)

            # 4. Calculate alignment boundaries
            total_grid_content_width = sum(column_widths) + total_col_gaps
            total_grid_content_height = sum(row_heights) + total_row_gaps

            match node.align:
                case CoshAlign.START:  start_y = y + node.padding
                case CoshAlign.CENTER: start_y = y + (node.height / 2) - (total_grid_content_height / 2)
                case CoshAlign.END:    start_y = y + node.height - node.padding - total_grid_content_height
                case _:  start_y = y + node.padding

            match node.justify:
                case CoshJustify.START:  start_x = x + node.padding
                case CoshJustify.CENTER: start_x = x + (node.width / 2) - (total_grid_content_width / 2)
                case CoshJustify.END:    start_x = x + node.width - node.padding - total_grid_content_width
                case _:  start_x = x + node.padding

            # 5. Position and expand FILL elements
            current_y = start_y
            for row_index, row in enumerate(rows):
                current_x = start_x
                
                for column_index, child in enumerate(row):
                    # Now that we have a concrete track size, give FILL elements their size allocation!
                    if child.width is CoshSizing.FILL:
                        child.width = column_widths[column_index] - (child.margin * 2)
                    if child.height is CoshSizing.FILL:
                        child.height = row_heights[row_index] - (child.margin * 2)

                    layout(child, current_x + child.margin, current_y + child.margin)
                    current_x += column_widths[column_index] + node.gap

                current_y += row_heights[row_index] + node.gap

        for child in absolute_children:
            layout(child, x + node.padding + child._x, y + node.padding + child._y)

def update(delta : float):
    for tween in CoshUI._active_tweens:
        tween.update(delta)

    completed = [tween for tween in CoshUI._active_tweens if tween.finished]

    CoshUI._active_tweens -= { t for t in CoshUI._active_tweens if t.finished }

    for tween in completed:
        if tween.on_complete is not None:
            tween.on_complete()

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
    if hasattr(node, 'overflow') and node.overflow is CoshOverflow.HIDDEN:
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

        if data.mouse_filter is CoshMouseFilter.IGNORE:
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
            if data.mouse_filter is CoshMouseFilter.STOP:
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
                if data.mouse_filter is CoshMouseFilter.STOP:
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