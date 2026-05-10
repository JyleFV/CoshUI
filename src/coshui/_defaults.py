from .animation import animate
from .engine import CoshUI
from .themes import CoshTheme
from .types import CoshSizing
from .utility import adjust_brightness_value

ENGINE_DEFAULTS = {
    "width": CoshSizing.AUTO,
    "height": CoshSizing.AUTO,
    "margin": 0.0,
    "padding": 0.0,
    "gap": 0.0,
    "alpha": 255,
    "border_radius": 0,
    "transform_scale": 1.0,
    "transform_position": (0, 0),
    "transform_rotation": 0.0,
    "font_size": 16,
    "text_color": (255, 255, 255),
}

# Button
# TODO: Use the colors in _state_storage and use a helper function to just adjust the values based on a factor.
def _button_default_hover(node_id):
    current = CoshUI.get_state(node_id, "background_color")

    original = CoshUI.get_state(node_id, "_orig_bg") or current
    if not CoshUI.get_state(node_id, "_orig_bg"):
        CoshUI.set_state(node_id, "_orig_bg", original)

    target = adjust_brightness_value(original, 1.2)
    animate("background_color", node_id, target, 0.075, "ease_in")

def _button_default_unhover(node_id):
    original = CoshUI.get_state(node_id, "_orig_bg")
    if original:
        animate("background_color", node_id, original, 0.075, "ease_in")

def _button_default_click(node_id):
    original = CoshUI.get_state(node_id, "_orig_bg")
    if original:
        target = adjust_brightness_value(original, 0.8)
        animate("background_color", node_id, target, 0.05, "ease_in")

def _button_default_release(node_id):
    original = CoshUI.get_state(node_id, "_orig_bg")
    if original:
        animate("background_color", node_id, original, 0.05, "ease_in")

# Checkbox
def _checkbox_default_hover(node_id):
    pass

def _checkbox_default_unhover(node_id):
    pass

def _checkbox_default_click(node_id):
    CoshUI.set_state(node_id, "checked", not CoshUI.get_state(node_id, "checked", False))