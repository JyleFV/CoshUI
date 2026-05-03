from .animation import animate

# Buttons
BUTTON_DEFAULT_STYLE = {
    "width" : 175,
    "height" : 65,
    "background_color" : (86, 115, 143),
    "border" : ((255, 255, 255), 2),
    "border_radius" : 20,
    "font_size" : 24
}

def _button_default_hover(node):
    animate("background_color", node, (119, 161, 201), 0.1, "ease_in")

def _button_default_unhover(node):
    animate("background_color", node, (86, 115, 143), 0.1, "ease_in")

def _button_default_click(node):
    animate("background_color", node, (60, 85, 110), 0.1, "ease_in")

def _button_default_release(node):
    animate("background_color", node, (119, 161, 201) if node._was_hovered else (86, 115, 143), 0.1, "ease_in")

# Labels
LABEL_DEFAULT_STYLE = {
    "width" : 175,
    "height" : 65,
    "font_size" : 24
}

__all__ = ["BUTTON_DEFAULT_STYLE", "LABEL_DEFAULT_STYLE", "_button_default_click", "_button_default_hover", "_button_default_release", "_button_default_unhover"]