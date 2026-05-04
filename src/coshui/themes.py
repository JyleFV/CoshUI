from dataclasses import dataclass, field

# ================ Theme ================

@dataclass
class CoshTheme:
    button : dict = field(default_factory=lambda: {...})
    label : dict = field(default_factory=lambda: {...})
    container : dict = field(default_factory=lambda: {...})
    checkbox : dict = field(default_factory=lambda: {...})
    image : dict = field(default_factory=lambda: {...})
    
def create_theme(theme : CoshTheme):
    pass

def set_theme(theme : CoshTheme):
    pass

# ================ Theme ================