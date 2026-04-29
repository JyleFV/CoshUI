from .cui_error import CoshUIError
import time

class CoshUI:
    _stack = []
    _node_map = {}
    _active_tweens = set()
    _style_dirty = set() 
    _font_library = {}
    _render_stack = []
    _style_class = {}
    _active_renderer = False
    _prev_ui_state = []
    _current_ui_state = []
    _default_font = None # TODO: Set this to a default font

class CoshUIRenderer:
    def __init__(self, backend):
        from .nodes import Container
        self.backend = backend
        self.root = Container()
        self._last_time = time.perf_counter()

    def __enter__(self):
        from .utility import update

        if CoshUI._active_renderer:
            raise CoshUIError("Cannot nest renderer objects.")
        
        now = time.perf_counter()
        delta = now - self._last_time
        self._last_time = now

        if delta > 0.1:
            delta = 1/60
        
        update(delta)

        # TODO: Add state diffing 
        CoshUI._active_renderer = True
        CoshUI._stack.clear()  
        CoshUI._node_map.clear() # TODO: Get rid of this once state diffing is added
        self.root.children.clear()
        CoshUI._stack.append(self.root)
        return self

    def __exit__(self, *args):
        from .utility import measure, layout, render
        CoshUI._stack.pop()
        CoshUI._active_renderer = False

        measure(self.root)
        layout(self.root, self.root.layout.true_position.x, self.root.layout.true_position.y)
        render(self.root)
        self.backend.flush(CoshUI._render_stack)
        CoshUI._render_stack.clear()

        # At the very end of the render
        CoshUI._prev_ui_state = CoshUI._current_ui_state