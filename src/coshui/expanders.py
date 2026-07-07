from .state import CoshUI
from .input import CoshInput
from .types import CoshPositioning, CoshStyling, CoshDirection, CoshMouseFilter, CoshAlign, CoshJustify, CoshSignals, CoshSizing
from .pipeline import measure, finalize_defaults
from ._defaults import ENGINE_DEFAULTS
from .widgets import Container, Label, Box, Slider, Modal, Dropdown

def register_exapanders():
    if all(composite_widget in CoshUI._expander_registry for composite_widget in (Slider,Modal, Dropdown)):
        return
    
    CoshUI._expander_registry[Slider] = _expand_slider
    CoshUI._expander_registry[Dropdown] = _expand_dropdown
    CoshUI._expander_registry[Modal] = _expand_modal

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

def _expand_dropdown(node):
    saved_stack = CoshUI._stack.copy()
    CoshUI._stack.clear()

    open = CoshUI.get_state(node.id, "open") or False
    selector_index = CoshUI.get_state(node.id, "selector_index") or node.selector_index
    node.font = CoshUI._font_library.get(node.font) if node.font is not None else CoshUI._default_font

    # Toggle open on selector click
    if CoshUI._focused_id == f"{node.id}::selector" and CoshUI._get_signal(f"{node.id}::selector", CoshSignals.CLICKED):
        open = not open
        CoshUI.set_state(node.id, "open", open)

    # Check if any item was clicked
    for i in range(len(node.item_list)):
        item_id = f"{node.id}::item_{i}"
        if CoshUI._focused_id == item_id and CoshUI._get_signal(item_id, CoshSignals.CLICKED):
            selector_index = i
            CoshUI.set_state(node.id, "selector_index", selector_index)
            CoshUI.set_state(node.id, "open", False)
            open = False
            if node.bind is not None:
                node.bind.value = node.item_list[selector_index]

    root = Container(
        id=f"{node.id}::root",
        direction=CoshDirection.COLUMN,
        z_index=node.z_index,
        width=node.width
    )

    selector = Container(
        id=f"{node.id}::selector",
        height=node.height,
        width=node.width,
        align=CoshAlign.CENTER,
        justify=CoshJustify.CENTER,
        style=CoshStyling(
            background_color=node.style.background_color,
            border_radius=node.style.border_radius,
            border=node.style.border,
            alpha=node.style.alpha
        ),
        z_index=node.z_index
    )

    selector_label = Label(
        id=f"{node.id}::selector_label",
        text=str(node.item_list[selector_index]),
        font=node.font,
        font_size=node.font_size,
        text_color=node.text_color,
        width=CoshSizing.AUTO,
        height=CoshSizing.AUTO,
        mouse_filter=CoshMouseFilter.PASS,
        z_index=node.z_index
    )

    selector.children.append(selector_label)
    root.children.append(selector)

    if open:
        options = [(i, item) for i, item in enumerate(node.item_list) if i != selector_index]

        selection = Container(
            id=f"{node.id}::selection_box",
            direction=CoshDirection.COLUMN,
            width=node.width,
            positioning=CoshPositioning.ABSOLUTE,
            y=node.height if node.height else ENGINE_DEFAULTS["height"],
            style=CoshStyling(
                background_color=node.style.background_color,
                border_radius=node.style.border_radius,
                border=node.style.border,
                alpha=node.style.alpha
            ),
            z_index=node.z_index + 1
        )

        for i, item in options:
            item_container = Container(
                id=f"{node.id}::item_{i}",
                width=node.width,
                height=node.height,
                align=CoshAlign.CENTER,
                justify=CoshJustify.CENTER,
                style=CoshStyling(
                    background_color=node.style.background_color,
                    border_radius=node.style.border_radius,
                    alpha=node.style.alpha
                ),
                z_index=node.z_index + 1
            )

            item_label = Label(
                id=f"{node.id}::item_label_{i}",
                text=str(item),
                font=node.font,
                font_size=node.font_size,
                text_color=node.text_color,
                width=CoshSizing.AUTO,
                height=CoshSizing.AUTO,
                mouse_filter=CoshMouseFilter.PASS,
                z_index=node.z_index + 1
            )

            item_container.children.append(item_label)
            selection.children.append(item_container)

        root.children.append(selection)

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