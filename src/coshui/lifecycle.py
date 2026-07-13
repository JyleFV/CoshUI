import difflib

from .cui_error import CoshUIError
from .state import CoshUI
from .types import CoshSizing, CoshPercentage

class CoshLifecycle:
    @staticmethod
    def register_node(node):
        if CoshUI._stack:
            CoshUI._stack[-1].children.append(node)
        
        CoshLifecycle.prepare_node(node)

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
                    raise CoshUIError(f"Class `{name}` doesn't exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")   
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
    def apply_theme(node):
        from .themes import get_for, resolve_token
        theme = CoshUI._active_theme

        theme_style = get_for(theme, node)
        if not theme_style or theme_style is None:
            return
        
        for key, value in theme_style.items():
            if hasattr(node, key) and getattr(node, key) is None:
                resolved_value = resolve_token(theme, value)
                setattr(node, key, resolved_value)
            if hasattr(node.style, key) and getattr(node.style, key) is None:
                resolved_value = resolve_token(theme, value)
                setattr(node.style, key, resolved_value)
    
    @staticmethod
    def expand(node):
        from .widgets import Modal
        for i, child in enumerate(node.children):
            if type(child) in CoshUI._expander_registry:
                if isinstance(child, Modal):
                    CoshLifecycle.expand(child)
                expander = CoshUI._expander_registry[type(child)]
                expanded = expander(child)
                node.children[i] = expanded
            else:
                CoshLifecycle.expand(child)
        
    @staticmethod
    def prepare_node(node):
        if node.id:
            if node.id in CoshUI._active_ids:
                raise CoshUIError(f"A node with id `{node.id}` already exists.")
            CoshUI._active_ids.add(node.id)
            CoshLifecycle.reconcile(node)
        
        CoshLifecycle.apply_styling(node)
        CoshLifecycle.apply_theme(node)
        CoshLifecycle.validate_node_types(node)

    # This method checks if every property is the correct datatype
    # A runtime type checker if you will.
    @staticmethod
    def validate_node_types(node):
        # Holds properties and their supposed types
        PROPERTY_RULES = {
            "width": (int, float, CoshSizing, CoshPercentage),
            "height": (int, float, CoshSizing, CoshPercentage),
            "margin": (int, float),
            "padding": (int, float),
            "gap": (int, float),
            "alpha": (int,),
            "border_radius": (int, float),
            "font_size": (int,),
            "transform_scale": (int, float),
            "transform_rotation": (int, float),
            "transform_position": (tuple,),
            "text_color": (tuple,),
            "background_color": (tuple,)
        }

        for target in (node, node.style):
            if not target:
                continue
                
            for property, allowed_types in PROPERTY_RULES.items():
                if not hasattr(target, property):
                    continue
                    
                val = getattr(target, property)
                if val is None:
                    continue
                
                if not isinstance(val, allowed_types):
                    node_name = node.id if node.id else type(node).__name__
                    expected = ", ".join([t.__name__ for t in allowed_types])
                    
                    raise CoshUIError(
                        f"Type Error on '{node_name}': Property `{property}` is set to `{val}` ({type(val).__name__}), "
                        f"but expected types are ({expected})."
                    )