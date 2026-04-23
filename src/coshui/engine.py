class CoshUI:
    _stack = []
    _node_map = {}
    _active_tweens = set()
    _style_dirty = set() 
    _font_library = {}
    _render_stack = []

class CoshUIRenderer:
    def __init__(self, backend):
        import time
        from .nodes import Container
        self.backend = backend
        self.root = Container()
        self._last_time = time.perf_counter()

    def __enter__(self):
        import time
        from .utility import update
        now = time.perf_counter()
        delta = now - self._last_time
        self._last_time = now

        update(delta)

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
        render(self.root, self.backend)
        self.backend.flush(CoshUI._render_stack)
        CoshUI._render_stack.clear()