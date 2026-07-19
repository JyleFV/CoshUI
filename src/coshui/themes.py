from dataclasses import dataclass, field
import difflib

from .cui_error import CoshUIError

@dataclass
class CoshTheme:
    """
    CoshTheme is the object that holds theme values.
    
    ### Attributes

    - **tokens**: Reusable values you can pass as values to Node properties (e.g. "primary_color" passed to a Button's "background_color" as "@primary_color"). 
    Do remember, when passing tokens as Node values, type "@" before the name of the token or else it will not be parsed as a token and may appear as an error.
    - **nodes**: The dictionary that holds all Node values. You can set default values for nodes here directly (e.g. dict(Button={ "background_color": (255, 0, 0) }), or pass in tokens (e.g. dict(Button={ "background_color": "@primary_color" }).
    
    When overriding the "nodes" property. Be sure to set the names EXACTLY as the widgets are named.
    """
    
    tokens: dict = field(default_factory=dict)
    nodes: dict = field(default_factory=dict)

    def __post_init__(self):
        MASTER_WIDGET_LIST = ['Container', 'Grid', 'Modal', 'Button', 'Label', 'RichLabel', 'Checkbox', 'Image', 'Dropdown', 'Slider']

        for node in self.nodes:
            if node not in MASTER_WIDGET_LIST:
                close_match = difflib.get_close_matches(node, MASTER_WIDGET_LIST, n=1)
                raise Exception(f"Unknown node `{node}` in theme configuration. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")

def get_for(theme: CoshTheme, node):
    node_name = node.__class__.__name__
    node_style = theme.nodes.get(node_name, None)

    if node_style is None:
        return None 

    return node_style

def resolve_token(theme: CoshTheme, token: str):
    if isinstance(token, str) and token.startswith("@"):
        token_value = theme.tokens.get(token[1:])
    
        if token_value is None:
            close_match = difflib.get_close_matches(token[1:], theme.tokens.keys(), n=1)
            raise CoshUIError.Main(f"Unknown theme token `{token}`. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")
        
        return token_value

    return token