from .animation import Tween, lerp_tuple

class TweenManager:
    def __init__(self):
        self.tween_registry = {}

    def register_tween(self, tween: Tween) -> Tween:
        key = (tween.target_id, tween.property)
        
        if key in self.tween_registry:
            existing_tween = self.tween_registry[key]
            if existing_tween.end_value == tween.end_value:
                return existing_tween
        
        from .state import CoshUI
        
        start_value = CoshUI.get_state(tween.target_id, tween.path)
        if start_value is None:
            start_value = tuple(0 for _ in tween.end_value) if tween.lerp_fn == lerp_tuple else 0.0
            
        tween.start_value = start_value

        self.tween_registry[key] = tween
        return tween

    def update(self, delta: float):
        completed_keys = []

        for key, tween in self.tween_registry.items():
            tween._update(delta)
            if tween._finished:
                completed_keys.append(key)

        for key in completed_keys:
            tween = self.tween_registry.pop(key, None)
            if tween and tween._on_complete is not None:
                tween._on_complete()
        

