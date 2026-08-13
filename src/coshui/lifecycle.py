import difflib

from .cui_error import CoshUIError
from .state import CoshUI
from .types import TupleLength

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

            if not isinstance(node.classes, (str, list, tuple)):
                raise CoshUIError.Main(f"Type Error for class in Node `{node.id if node.id is not None else type(node).__name__}`. Ecxpected `(str, list, tuple)` but got `{type(node.classes).__name__}`.")
            class_names = node.classes.split() if isinstance(node.classes, str) else node.classes

            merged_style = CoshStyling()
            for name in class_names:
                if name not in CoshUI._style_class.keys():
                    close_match = difflib.get_close_matches(name, CoshUI._style_class.keys(), n=1)
                    raise CoshUIError.Main(f"Class `{name}` doesn't exist. Did you mean `{close_match[0] if close_match else 'Unknown'}`?")   
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
                raise CoshUIError.Main(f"A node with id `{node.id}` already exists.")
            CoshUI._active_ids.add(node.id)
            CoshLifecycle.reconcile(node)
        
        CoshLifecycle.apply_styling(node)
        CoshLifecycle.apply_theme(node)
        CoshLifecycle.validate_node_types(node)

    @staticmethod
    def validate_node_types(node):
        from ._defaults import ENGINE_DEFAULTS

        for target, type_map in ((node, node.valid_property_types()), (node.style, node.style.valid_property_types())):
            for property, allowed_types in type_map.items():
                if not hasattr(target, property):
                    continue

                val = getattr(target, property)

                if val is None:
                    if property in ENGINE_DEFAULTS or type(None) in allowed_types:
                        continue
                    node_name = node.id if node.id else type(node).__name__
                    raise CoshUIError.Main(
                        f"Type Error on {type(node).__name__} Widget with name '{node_name}': Property `{property}` cannot be None."
                    )

                # Split length-constrained checks from plain isinstance checks
                length_checks = [t for t in allowed_types if isinstance(t, TupleLength)]
                plain_types = tuple(t for t in allowed_types if not isinstance(t, TupleLength))

                is_valid = False
                if length_checks and any(lc.matches(val) for lc in length_checks):
                    is_valid = True
                elif plain_types:
                    is_invalid_bool = isinstance(val, bool) and bool not in plain_types
                    is_valid = isinstance(val, plain_types) and not is_invalid_bool

                if not is_valid:
                    node_name = node.id if node.id else type(node).__name__
                    expected_parts = [t.__name__ if t is not type(None) else "None" for t in plain_types]
                    expected_parts += [lc.label for lc in length_checks]
                    expected = ", ".join(expected_parts)

                    raise CoshUIError.Main(
                        f"Type Error on {type(node).__name__} Widget with name '{node_name}': Property `{property}` is set to `{val}` ({type(val).__name__}), but expected types are ({expected})."
                    )