from .animation import Tween, lerp_tuple

# Deals with Tween creation, storage, lifetime, and updates.
class TweenManager:
    def __init__(self):
        self.tween_registry: dict[tuple, Tween] = {}

    def create_tween(self, n_property, target_id, end_value, duration, easing, path, lerp_fn):
        from .state import CoshUI
        key = (target_id, n_property)

        if key in self.tween_registry:
            existing = self.tween_registry[key]
            if not existing._finished and (existing.end_value == end_value or existing._ping_pong):
                return existing

        start_value = CoshUI.get_state(target_id, path)
        if start_value is None:
            start_value = tuple(0 for _ in end_value) if lerp_fn == lerp_tuple else 0.0

        tween = Tween(n_property, target_id, start_value, end_value, duration, easing, path, lerp_fn)
        
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
        

