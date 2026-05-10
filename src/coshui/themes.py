from dataclasses import dataclass, field
import difflib

from .cui_error import CoshUIError

# ================ Theme ================

@dataclass
class CoshTheme:
    button : dict = field(default_factory=lambda: {...})
    label : dict = field(default_factory=lambda: {...})
    container : dict = field(default_factory=lambda: {...})
    modal : dict = field(default_factory=lambda: {...})
    checkbox : dict = field(default_factory=lambda: {...})
    image : dict = field(default_factory=lambda: {...})
    slider : dict = field(default_factory=lambda: {...})

    def get_for(self, node):
        from .nodes import Container, Modal
        from .widgets import Button, Label, Checkbox, Image, Slider

        if isinstance(node, Container):
            return self.container
        if isinstance(node, Modal):
            return self.modal
        if isinstance(node, Button): 
            return self.button
        if isinstance(node, Label):
            return self.label
        if isinstance(node, Checkbox):
            return self.checkbox
        if isinstance(node, Image):
            return self.image
        if isinstance(node, Slider):
            return self.slider

        return None
    
def create_theme(name : str, theme : CoshTheme):
    from .engine import CoshUI
    CoshUI._theme_registry[name] = theme

def set_theme(theme_name : str):
    from .engine import CoshUI
    theme = CoshUI._theme_registry.get(theme_name, None)
    if theme is None:
        close_match = difflib.get_close_matches(theme_name, CoshUI._theme_registry.keys(), n=1)
        raise CoshUIError(f"The theme `{theme_name}` does not exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
    CoshUI._active_theme = theme

# ================ Theme ================