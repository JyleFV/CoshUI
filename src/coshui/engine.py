from .cui_error import CoshUIError
from .backend import CoshBackend
import time

class CoshUI:
    _stack = []
    _node_map = {}
    _active_ids = set()
    _active_tweens = set()
    _style_dirty = set() 
    _font_library = {}
    _render_stack = []
    _style_class = {}
    _active_renderer = False
    _default_font = None # TODO: Set this to a default font
    _last_time : float = 0.0

class CoshUIRenderer:
    def __init__(self, backend : CoshBackend):
        from .nodes import Container
        self.backend = backend
        screen_w, screen_h = self.backend.get_size()
        self.root = Container()

    def __enter__(self):
        from .utility import update

        if CoshUI._active_renderer:
            raise CoshUIError("Cannot nest renderer objects.")
        
        now = time.perf_counter()

        if CoshUI._last_time == 0.0:
            delta = 1/60
        else:
            delta = now - CoshUI._last_time
        
        CoshUI._last_time = now

        if delta > 0.1:
            delta = 1/60
        
        update(delta)

        CoshUI._active_renderer = True
        CoshUI._active_ids.clear()
        CoshUI._stack.clear()  
        self.root.children.clear()
        CoshUI._stack.append(self.root)
        return self

    def __exit__(self, *args):
        from .utility import measure, layout, render
        CoshUI._stack.pop()
        CoshUI._active_renderer = False

        measure(self.root)
        layout(self.root, self.root.layout.true_position[0], self.root.layout.true_position[1]) # index 0 is x, index 1 is y
        render(self.root)
        CoshUI._render_stack.sort(key=lambda d: d.z_index)
        self.backend.flush(CoshUI._render_stack)
        CoshUI._render_stack.clear()

        # Clean up stale nodes
        stale = set(CoshUI._node_map.keys()) - CoshUI._active_ids
        for key in stale:
            del CoshUI._node_map[key]
