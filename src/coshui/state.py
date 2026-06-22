from __future__ import annotations
from typing import TYPE_CHECKING
import os

from .themes import CoshTheme
from .tween_manager import TweenManager

if TYPE_CHECKING:
    from .debug import CoshDebug

# TODO: Separate Composite Widgets 
# ex. 
# slider={ "thumb" : {...}, "track" : {...} } 
# modal={ "root" : {...}, "header" : {...}, "content" : {...} }

# DEFAULT VALUES
DEFAULT_THEME = CoshTheme(
            button={ "width" : 100, "height" : 30, "background_color" : (86, 115, 143), "border" : ((255, 255, 255), 1), "border_radius" : 5, "font_size" : 18 },
            label={ "font_size" : 18 },
            checkbox={ "width" : 25, "height" : 25, "border_radius" : 4, "border": ((200, 200, 200), 2), "checked_color" : (85, 75, 255), "unchecked_color" : (200, 200, 200)},
            image={ "width" : 150, "height" : 150 },
            modal={ "header_color" : (60, 60, 80), "header_border_radius" : (7.5, 7.5, 0, 0), "content_color" : (80, 80, 100), "content_border_radius" : (0, 0, 7.5, 7.5) }, 
            slider={ "thumb_color" : (100, 100, 100), "track_color" : (200, 200, 200), "border_radius" : 50 },
            dropdown={ "width" : 150, "height" : 30, "background_color" : (100, 100, 100) }
        )

COURIER = os.path.join(os.path.dirname(__file__), "assets", "fonts", "CourierPrime.ttf")
INTER = os.path.join(os.path.dirname(__file__), "assets", "fonts", "Inter.ttf")
UBUNTUMONO = os.path.join(os.path.dirname(__file__), "assets", "fonts", "UbuntuMono.ttf")

class CoshUI:
    #----------------  Lifecycle ----------------
    _stack : list = []
    _active_ids : set = set()
    _active_renderer : bool = False
    _last_time : float = 0.0
    _widget_counter : int = 0
    _state_storage : dict = {} # FORMAT: { node_id : { "example_color": (255, 255, 255) }, node_id : {} }
    # ---------------- Render-related ----------------
    _font_library : dict = { "Courier" : COURIER, "Inter" : INTER, "Ubuntu" : UBUNTUMONO }
    _render_stack : list = []
    _default_font : str = _font_library.get("Inter")
    # ---------------- Composite Widgets ----------------
    _expander_registry : dict = {}
    # ---------------- Input & Event-related ----------------
    _focused_id = None
    _signals : dict = {} # FORMAT: { node_id : set() }
    _tween_manager : TweenManager = TweenManager()
    # ---------------- Theme-related ----------------
    _theme_registry : dict = { "DEFAULT" : DEFAULT_THEME }
    _active_theme = _theme_registry.get("DEFAULT")
    # ----------------Class System ----------------
    _style_class : dict = {}
    # ---------------- Text Measuring ----------------
    _measure_text : callable = None
    # ---------------- Debug ----------------
    _debugger : None | CoshDebug = None

    @classmethod
    def get_state(cls, node_id, key, default=None):
        return cls._state_storage.get(node_id, {}).get(key, default)

    @classmethod
    def set_state(cls, node_id, key, value):
        if not node_id in cls._state_storage:
            cls._state_storage[node_id] = {}
        cls._state_storage[node_id][key] = value
    
    @classmethod
    def _emit_signal(cls, node_id, signal):
        if node_id not in cls._signals:
            cls._signals[node_id] = set()
        cls._signals[node_id].add(signal)

    @classmethod
    def _get_signal(cls, node_id, signal):
        return signal in cls._signals.get(node_id, set())