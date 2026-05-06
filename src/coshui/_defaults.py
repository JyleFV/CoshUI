from .animation import animate
from .engine import CoshUI
from .themes import CoshTheme

ENGINE_DEFAULTS = {
    "width": 0.0,
    "height": 0.0,
    "margin": 0.0,
    "padding": 0.0,
    "gap": 0.0,
    "alpha": 255,
    "border_radius": 0,
    "transform_scale": 1.0,
    "transform_rotation": 0.0,
    "font_size": 16,
    "text_color": (255, 255, 255),
}

ENGINE_DEFAULT_THEME = CoshTheme(
        button={ "width" : 100, "height" : 30, "background_color" : (86, 115, 143), "border" : ((255, 255, 255), 1), "border_radius" : 5, "font_size" : 18 },
        label={ "width" : 175, "height" : 65, "font_size" : 18 },
        container={},
        checkbox={ "width" : 25, "height" : 25, "checked_color" : (85, 75, 255), "unchecked_color" : (200, 200, 200)},
        image={ "width" : 150, "height" : 150 }
    )

# Button
def _button_default_hover(node_id):
    animate("background_color", node_id, (117, 156, 195), 0.1, "ease_in")

def _button_default_unhover(node_id):
    animate("background_color", node_id, (86, 115, 143), 0.1, "ease_in")

def _button_default_click(node_id):
    animate("background_color", node_id, (60, 85, 110), 0.1, "ease_in")

def _button_default_release(node_id):
    animate("background_color", node_id, (119, 161, 201), 0.1, "ease_in")

# Checkbox
def _checkbox_default_hover(node_id):
    pass

def _checkbox_default_unhover(node_id):
    pass

def _checkbox_default_click(node_id):
    CoshUI.set_state(node_id, "checked", not CoshUI.get_state(node_id, "checked", False))