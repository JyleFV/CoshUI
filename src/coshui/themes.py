from dataclasses import dataclass, field

# ================ Theme ================

@dataclass
class CoshTheme:
    button : dict = field(default_factory=lambda: {...})
    label : dict = field(default_factory=lambda: {...})
    container : dict = field(default_factory=lambda: {...})
    checkbox : dict = field(default_factory=lambda: {...})
    image : dict = field(default_factory=lambda: {...})

    def get_for(self, node):
        from .nodes import Container
        from .widgets import Button, Label, Checkbox, Image

        if isinstance(node, Container):
            return self.container
        if isinstance(node, Button): 
            return self.button
        if isinstance(node, Label):
            return self.label
        if isinstance(node, Checkbox):
            return self.checkbox
        if isinstance(node, Image):
            return self.image

        return None
    
def create_theme(theme : CoshTheme):
    pass

def set_theme(theme : CoshTheme):
    pass

# ================ Theme ================