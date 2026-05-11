from dataclasses import dataclass, field
import difflib

from .cui_error import CoshUIError

# ================ Theme ================

@dataclass
class CoshTheme:
    button : dict = field(default_factory=lambda: {...})
    label : dict = field(default_factory=lambda: {...})
    modal : dict = field(default_factory=lambda: {...})
    checkbox : dict = field(default_factory=lambda: {...})
    image : dict = field(default_factory=lambda: {...})
    slider : dict = field(default_factory=lambda: {...})

    def get_for(self, node):
        from .widgets import Modal, Button, Label, Checkbox, Image, Slider
        
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

# ================ Theme ================