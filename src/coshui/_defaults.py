from .animation import animate
from .engine import CoshUI
from .utility import adjust_color

# Button
def _button_default_hover(node):
    animate("background_color", node, adjust_color(CoshUI._active_theme.button["background_color"], 1.5), 0.1, "ease_in")

def _button_default_unhover(node):
    animate("background_color", node, (86, 115, 143), 0.1, "ease_in")

def _button_default_click(node):
    animate("background_color", node, (60, 85, 110), 0.1, "ease_in")

def _button_default_release(node):
    animate("background_color", node, (119, 161, 201) if node._was_hovered else (86, 115, 143), 0.1, "ease_in")

# Checkbox
def _checkbox_default_hover(node):
    pass

def _checkbox_default_unhover(node):
    pass

def _checkbox_default_click(node):
    node.checked = not node.checked