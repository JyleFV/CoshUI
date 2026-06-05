from abc import ABC, abstractmethod
from enum import Enum

from ...input import CoshInput

try:
    import moderngl_window
except ImportError:
    moderngl_window = None

try:
    import glfw
except ImportError:
    glfw = None

class _WindowDriver(ABC):
    @abstractmethod
    def _measure_text(self, text, font_path, font_size):
        pass
    
    @abstractmethod
    def _poll_input(self):
        pass
    
    @abstractmethod
    def _get_size(self):
        pass

# GLFW
class _GLFWDriver(_WindowDriver):
    def _measure_text(self):
        pass

    def _poll_input(self):
        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = glfw.get_cursor_pos(glfw.get_current_context())
        CoshInput._mouse_delta = (
            CoshInput._mouse_position[0] - CoshInput._prev_mouse_position[0],
            CoshInput._mouse_position[1] - CoshInput._prev_mouse_position[1]
        )
        CoshInput._prev_mouse_position = CoshInput._mouse_position
        CoshInput._current_mouse_pressed = glfw.get_mouse_button(glfw.get_current_context(), glfw.MOUSE_BUTTON_LEFT) is glfw.PRESS

    def _get_size(self):
        return glfw.get_window_size(glfw.get_current_context())

# MGLW
class _MGLWDriver(_WindowDriver):
    def _measure_text(self):
        pass

    # This works only if _calc_mouse_delta(self.mouse_x, self.mouse_y) is called beforehand
    # or if _mouse_pos is set somewhere. Either way, MGLW hates others making tooling around it seems.
    def _poll_input(self):
        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = moderngl_window.window()._mouse_pos
        CoshInput._mouse_delta = (
            CoshInput._mouse_position[0] - CoshInput._prev_mouse_position[0],
            CoshInput._mouse_position[1] - CoshInput._prev_mouse_position[1]
        )
        CoshInput._prev_mouse_position = CoshInput._mouse_position
        CoshInput._current_mouse_pressed = moderngl_window.window()._mouse_buttons.left

    def _get_size(self):
        return moderngl_window.window().size

class Windower(Enum):
    GLFW = _GLFWDriver
    MGLW = _MGLWDriver