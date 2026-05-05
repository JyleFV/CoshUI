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
    #----------------  Lifecycle ----------------
    _stack : list = []
    _active_ids : set = set()
    _active_renderer : bool = False
    _last_time : float = 0.0
    _widget_counter : int = 0
    _state_storage : dict = {} # New source of truth FORMAT: { node_id : { "example_color": (255, 255, 255) }, node_id : {} }
    # ---------------- Render-related ----------------
    _style_dirty : set = set() 
    _temp_paths : set = set()
    _font_library : dict = {}
    _render_stack : list = []
    _default_font : str = os.path.join(os.path.dirname(__file__), "assets", "fonts", "inter.ttf")
    # ---------------- Input & Event-related ----------------
    _focused_id = None
    _action_map : dict = {} # For events
    _active_tweens : set = set()
    # ---------------- Theme-related ----------------
    _theme_registry : dict = {}
    _active_theme = CoshTheme(
        button={ "width" : 100, "height" : 30, "background_color" : (86, 115, 143), "border" : ((255, 255, 255), 1), "border_radius" : 5, "font_size" : 18 },
        label={ "width" : 175, "height" : 65, "font_size" : 18 },
        container={},
        checkbox={ "width" : 25, "height" : 25, "checked_color" : (85, 75, 255), "unchecked_color" : (200, 200, 200)},
        image={ "width" : 150, "height" : 150 }
    )
    # ----------------Class System ----------------
    _style_class : dict = {}
    
    @classmethod
    def get_state(cls, node_id, key, default=None):
        return cls._state_storage.get(node_id, {}).get(key, default)

    @classmethod
    def set_state(cls, node_id, key, value):
        if not node_id in cls._state_storage:
            cls._state_storage[node_id] = {}
        cls._state_storage[node_id][key] = value

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

        CoshLifecycle.bake(self.root)

        measure(self.root)
        layout(self.root, self.root.layout.true_position[0], self.root.layout.true_position[1]) # index 0 is x, index 1 is y
        render(self.root)

        CoshUI._render_stack.sort(key=lambda d: d.z_index)
        process_events()
        self.backend.flush(CoshUI._render_stack)

        CoshUI._action_map.clear()
        CoshUI._render_stack.clear()

        # Clean up stale nodes
        stale = set(CoshUI._state_storage.keys()) - CoshUI._active_ids
        for key in stale:
            del CoshUI._state_storage[key]

class CoshLifecycle:
    @staticmethod
    def register_node(node):
        if CoshUI._stack:
            CoshUI._stack[-1].children.append(node)
        
        if node.id:
            if node.id in CoshUI._active_ids:
                raise CoshUIError(f"A node with id `{id}` already exists.")
            CoshUI._active_ids.add(node.id)
            CoshLifecycle.reconcile(node)
            CoshLifecycle.register_events(node)

        CoshLifecycle.apply_theme(node)
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
    
    @staticmethod
    def reconcile(node):
        stored = CoshUI._state_storage.get(node.id, {})
        if stored:
            for key, value in stored.items():
                if hasattr(node.style, key):
                    setattr(node.style, key, value)
                elif hasattr(node, key):
                    setattr(node, key, value)
            else:
                CoshUI._state_storage[node.id] = {
                    "background_color": node.style.background_color,
                    "alpha": node.style.alpha,
                    "transform_position": node.style.transform_position,
                    "transform_scale": node.style.transform_scale,
                    "transform_rotation": node.style.transform_rotation,
                    "_was_hovered": node._was_hovered
                }

    @staticmethod
    def register_events(node):
        events = ["on_click", "on_release", "on_hover", "on_unhover"]
        node_events = {}

        for event in events:
            callback = getattr(node, event, None)
            if callable(callback):
                node_events[event] = callback

        if node_events:
            CoshUI._action_map[node.id] = node_events

    @staticmethod
    def apply_theme(node):
        from .widgets import Checkbox
        theme = CoshUI._active_theme

        theme_style = theme.get_for(node)
        if not theme_style or theme_style is None:
            return
        
        for key, value in theme_style.items():
            if hasattr(node.style, key) and getattr(node.style, key) is None:
                setattr(node.style, key, value)
            if hasattr(node.layout, key) and getattr(node.layout, key) is None:
                setattr(node.layout, key, value)
            if hasattr(node, key) and getattr(node, key) is None:
                setattr(node, key, value)
        
        if isinstance(node, Checkbox):
            if node.checked:
                node.style.background_color = node.checked_color
            else:
                node.style.background_color = node.unchecked_color

    @staticmethod
    def bake(node):
        from ._defaults import ENGINE_DEFAULTS
        # Check the three places data lives: Node, Style, Layout
        targets = [node, node.style, node.layout]
        
        for key, fallback in ENGINE_DEFAULTS.items():
            for target in targets:
                # We only apply the fallback if the attribute exists AND is None
                if hasattr(target, key) and getattr(target, key) is None:
                    setattr(target, key, fallback)

        if node.id:
            if node.id not in CoshUI._state_storage:
                CoshUI._state_storage[node.id] = {}

            CoshUI._state_storage[node.id].update({
                "background_color": node.style.background_color,
                "alpha": node.style.alpha,
                "transform_position": node.style.transform_position,
                "transform_scale": node.style.transform_scale,
                "transform_rotation": node.style.transform_rotation,
                "_was_hovered": node._was_hovered
            })

        # Clean the entire tree
        for child in node.children:
            CoshLifecycle.bake(child)