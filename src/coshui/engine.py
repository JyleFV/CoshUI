"""CoshUI module for the global and main processes of the UI Engine.

Set the main loop of the UI tree with CoshUIRenderer where every process
runs within its __enter__ and __exit__ dunder operators.

The CoshUI global namespace is private and should only be accessed 
by internal code, never outside."""

import time
import os
import difflib

from .cui_error import CoshUIError
from .backend import CoshBackend
from .themes import CoshTheme

class CoshUI:
    # Lifecycle
    _stack : list = []
    _node_map : dict = {}
    _active_ids : set = set()
    _active_tweens : set = set()
    _active_renderer : bool = False
    _last_time : float = 0.0
    _widget_counter : int = 0
    _state_storage : dict = {}

    # Render-related
    _style_dirty : set = set() 
    _temp_paths : set = set()
    _font_library : dict = {}
    _render_stack : list = []
    _default_font : str = os.path.join(os.path.dirname(__file__), "assets", "fonts", "inter.ttf")

    # Input-related
    _focused_node = None

    # Theme-related
    _theme_registry : dict = {}
    _active_theme = CoshTheme(
        button={ "width" : 100, "height" : 30, "background_color" : (86, 115, 143), "border" : ((255, 255, 255), 1), "border_radius" : 5, "font_size" : 18 },
        label={ "width" : 175, "height" : 65, "font_size" : 18 },
        container={},
        checkbox={ "width" : 25, "height" : 25, "checked" : (85, 75, 255), "unchecked" : (200, 200, 200)},
        image={ "width" : 150, "height" : 150 }
    )
    
    # Class System
    _style_class : dict = {}
    
    @classmethod
    def get_state(cls, node_id, key, default=None):
        return cls._state_storage.get(node_id, {}).get(key, default)

    @classmethod
    def set_state(cls, node_id, key, value):
        if not node_id in cls._state_storage:
            cls._state_storage[node_id] = {}
        cls._state_storage[node_id][key] = value

class CoshLifecycle:
    @staticmethod
    def register_node(node):
        if CoshUI._stack:
            CoshUI._stack[-1].children.append(node)
        
        if node.id:
            if node.id in CoshUI._active_ids:
                raise CoshUIError(f"A node with id `{id}` already exists.")
            CoshUI._active_ids.add(node.id)
            CoshUI._node_map[node.id] = node
        
        CoshLifecycle.apply_styling(node)

    @staticmethod
    def apply_styling(node):
        if node.classes:
            from .utility import merge_styles
            from .types import CoshStyling
            class_names = node.classes.split() if isinstance(node.classes, str) else node.classes

            merged_style = CoshStyling()
            for name in class_names:
                if name not in CoshUI._style_class.keys():
                    close_match = difflib.get_close_matches(name, CoshUI._style_class.keys(), n=1)
                    raise CoshUIError(f"Class `{name}` doesn't exist. Did you mean `{close_match[0] if close_match else "Unknown"}`?")   
                merged_style = merge_styles(merged_style, CoshUI._style_class.get(name))

            node.style = merge_styles(merged_style, node.style)

class CoshUIRenderer:
    def __init__(self, backend : CoshBackend):
        from .nodes import Container
        from .types import CoshSizing
        self.backend = backend
        screen_w, screen_h = self.backend.get_size()
        self.root = Container(sizing=CoshSizing.FIXED, width=screen_w, height=screen_h)

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
        self.backend.poll_input()

        CoshUI._active_renderer = True
        CoshUI._active_ids.clear()
        CoshUI._widget_counter = 0
        CoshUI._stack.clear()  
        self.root.children.clear()
        CoshUI._stack.append(self.root)

        return self

    def __exit__(self, *args):
        from .utility import measure, layout, render, process_events
        CoshUI._stack.pop()
        CoshUI._active_renderer = False

        measure(self.root)
        layout(self.root, self.root.layout.true_position[0], self.root.layout.true_position[1]) # index 0 is x, index 1 is y
        render(self.root)

        CoshUI._render_stack.sort(key=lambda d: d.z_index)
        process_events()
        self.backend.flush(CoshUI._render_stack)
        CoshUI._render_stack.clear()

        # Clean up stale nodes
        stale = set(CoshUI._node_map.keys()) - CoshUI._active_ids
        for key in stale:
            del CoshUI._node_map[key]
