from dataclasses import dataclass, field
import difflib

from .cui_error import CoshUIError

# ================ Theme ================

@dataclass
class CoshTheme:
    button: dict = field(default_factory=lambda: {...})
    label: dict = field(default_factory=lambda: {...})
    modal: dict = field(default_factory=lambda: {...})
    checkbox: dict = field(default_factory=lambda: {...})
    image: dict = field(default_factory=lambda: {...})
    slider: dict = field(default_factory=lambda: {...})
    dropdown: dict = field(default_factory=lambda: {...})

    def get_for(self, node):
        from .widgets import Modal, Button, Label, Checkbox, Image, Slider, Dropdown
        
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
        if isinstance(node, Dropdown):
            return self.dropdown

        return None

# NOTE: Rework in Progress
@dataclass
class _CoshTheme:
    """
    CoshTheme is the object that holds all default theme values.
    
    Attributes

    - tokens: Reusable values you can pass as values to Node properties (e.g. "primary_color" passed to a Button's "background_color" as "@primary_color"). 
    Do remember, when passing tokens as Node values, type "@" before the name of the token or else it will not be parsed as a token and may appear as an error.

    - nodes: The dictionary that holds all Node values. You can set default values for nodes here directly (e.g. dict(Button={ "background_color": (255, 0, 0) }), or pass in tokens (e.g. dict(Button={ "background_color": "@primary_color" }).
    
    When overriding the "nodes" property. Be sure to set the names EXACTLY as
    the widgets are named.
    """
    
    tokens: dict = field(default_factory=lambda: {...})
    nodes: dict = field(default_factory=lambda: {...})

def get_for(theme: _CoshTheme, node):
    node_style = theme.nodes.get(node.__class__.__name__, None)
    if node_style is None:
        raise CoshUIError(f"The node passed into CoshTheme for the node `{node.__class__.__name__}` seems to be wrong or doesn't exist...")

    return node_style

def resolve_token(theme: _CoshTheme, token: str):
    if token and token.startswith("@"):
        token_value = theme.tokens.get(token[1:])
    
        if token_value is None:
            close_match = difflib.get_close_matches(token[1:], theme.tokens.keys(), n=1)
            raise CoshUIError(f"Unknown theme token `{token}`. Did you mean `{close_match if close_match else 'Unknown'}`?")
        
        return token_value

    raise CoshUIError(f"Token `{token}` is not a real token. Please enter a token that starts with `@`.")
# ================ Theme ================