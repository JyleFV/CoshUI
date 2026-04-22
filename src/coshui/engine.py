from .nodes import Container
from .utility import measure, layout, render

class CoshUI:
    _stack = []
    _node_map = {}
    _active_tweens = set()
    _style_dirty = set()

class CoshUIRenderer:
    def __init__(self, backend):
        self.backend = backend
        self.root = Container
    
    def __enter__(self):
        CoshUI._stack.append(self.root)
        return self

    def __exit__(self, *args):
        CoshUI._stack.pop()
        
        # measure(self.root)
        # layout(self.root)
        # render(self.root, self.backend)
