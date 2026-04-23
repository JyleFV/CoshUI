class CoshUI:
    _stack = []
    _node_map = {}
    _active_tweens = set()
    _style_dirty = set() 
    _font_library = {}
    _render_stack = []

class CoshUIRenderer:
    def __init__(self, backend):
        from .nodes import Container
        self.backend = backend
        self.root = Container()

    def __enter__(self):
        CoshUI._stack.clear() # Just to make SURE that stack is fully cleared
        CoshUI._node_map.clear()
        self.root.children.clear()

        CoshUI._stack.append(self.root)
        return self

    def __exit__(self, *args):
        from .utility import measure, layout, render
        CoshUI._stack.pop()
        
        # measure(self.root)
        # layout(self.root)
        # update(delta)
        render(self.root, self.backend)
        self.backend.flush(CoshUI._render_stack)
        CoshUI._render_stack.clear()