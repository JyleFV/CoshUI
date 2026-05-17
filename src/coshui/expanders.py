from .state import CoshUI
from .input import CoshInput
from .types import CoshPositioning, CoshStyling, CoshDirection, CoshMouseFilter, CoshAlign
from .pipeline import measure, finalize_defaults
from ._defaults import ENGINE_DEFAULTS
from .lifecycle import CoshLifecycle
from .widgets import Container, Box

def _expand_slider(node):
    saved_stack = CoshUI._stack.copy()
    CoshUI._stack.clear()

    value = CoshUI.get_state(node.id, "value") or (node.value if node.value is not None else node.min_value)
    
    # Handle drag
    if CoshUI._focused_id == f"{node.id}::thumb" and CoshInput.get_mouse_down():
        delta_x = CoshInput._mouse_delta[0]
        value_range = node.max_value - node.min_value
        value_change = (delta_x / node.width) * value_range
        value = max(node.min_value, min(node.max_value, value + value_change))
        # snap to step
        value = round(value / node.step) * node.step
        CoshUI.set_state(node.id, "value", value)
        if node.bind:
            node.bind.value = value

    ratio = (value - node.min_value) / (node.max_value - node.min_value)
    # "It ain't much but it's honest work" - Terrarizer May 15, 2026
    # Nah but seriously though, why is this so ugly 🤮
    thumb_size = node.thumb_size if node.thumb_size is not None else node.height if node.height is not None else ENGINE_DEFAULTS["thumb_size"]
    thumb_x = ratio * (node.width - thumb_size)

    thumb = Box(
        id=f"{node.id}::thumb",
        width=thumb_size,
        height=thumb_size,
        x=thumb_x,
        positioning=CoshPositioning.ABSOLUTE,
        style=CoshStyling(background_color=node.thumb_color, border_radius=node.style.border_radius),
        z_index=node.z_index
    )

    track = Container(
        id=f"{node.id}::track",
        width=node.width,
        height=node.height if node.height else thumb_size,
        style=CoshStyling(background_color=node.track_color, border_radius=node.style.border_radius),
        align=CoshAlign.CENTER,
        z_index=node.z_index
    )

    track.children.append(thumb)
    CoshUI._stack = saved_stack
    return track

# TODO: Too lazy to work on this right now so I'll leave a todo for now.
def _expand_dropdown(node):
    saved_stack = CoshUI._stack.copy()
    CoshUI._stack.clear()

    root = Container(id=f"{node.id}::root")

    selector = Container(id=f"{node.id}::selector")

    children = []
    for i in range(len(node.list)):
        item = Container(id=f"{node.id}::item_{i}")
        children.append(item)

    selector.children.extend(children)

    root.children.append(selector)

    CoshUI._stack = saved_stack
    return root

def _expand_modal(node):
    saved_stack = CoshUI._stack.copy()
    CoshUI._stack.clear()

    pos = CoshUI.get_state(node.id, "drag_pos") or (0, 0)

    if CoshUI._focused_id == f"{node.id}::header" and CoshInput.get_mouse_down():
        pos = (
            pos[0] + CoshInput._mouse_delta[0],
            pos[1] + CoshInput._mouse_delta[1]
        )
        CoshUI.set_state(node.id, "drag_pos", pos)

    root = Container(
        id=f"{node.id}::root",
        direction=CoshDirection.COLUMN,
        x=pos[0],
        y=pos[1],
        positioning=node.positioning,
        z_index=node.z_index,
        mouse_filter=CoshMouseFilter.PASS
    )

    header = Container(
        id=f"{node.id}::header",
        width=node.width,
        height=25,
        padding=10,
        style=CoshStyling(background_color=node.header_color, border_radius=node.header_border_radius, alpha=node.style.alpha)
    )

    content = Container(
        id=f"{node.id}::content",
        direction=node.direction,
        width=node.width,
        height=node.height,
        align=node.align,
        justify=node.justify,
        gap=node.gap,
        padding=node.padding,
        style=CoshStyling(background_color=node.content_color, border_radius=node.content_border_radius, alpha=node.style.alpha),
        overflow=node.overflow
    )

    content.children.extend(node.children)

    finalize_defaults(content)
    measure(content)

    header.width = content.width

    root.children.append(header)
    root.children.append(content)

    CoshUI._stack = saved_stack
    return root