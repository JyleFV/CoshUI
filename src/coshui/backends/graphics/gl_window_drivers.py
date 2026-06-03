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
    def _measure_text(self):
        pass
    
    @abstractmethod
    def _poll_input(self):
        pass
    
    @abstractmethod
    def _get_size(self):
        pass

    @abstractmethod
    def _get_ortho_projection(self):
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
        CoshInput._current_mouse_pressed = True if glfw.get_mouse_button(glfw.get_current_context(), glfw.MOUSE_BUTTON_LEFT) is glfw.PRESS else False

    def _get_size(self):
        return glfw.get_window_size(glfw.get_current_context())

    def _get_ortho_projection(self):
        pass

# MGLW
class _MGLWDriver(_WindowDriver):
    def _measure_text(self):
        pass

    def _poll_input(self):
        CoshInput._prev_mouse_pressed = CoshInput._current_mouse_pressed
        CoshInput._mouse_position = moderngl_window.window()._mouse_pos # Doesn't seem to work.
        CoshInput._mouse_delta = (
            CoshInput._mouse_position[0] - CoshInput._prev_mouse_position[0],
            CoshInput._mouse_position[1] - CoshInput._prev_mouse_position[1]
        )
        CoshInput._prev_mouse_position = CoshInput._mouse_position
        CoshInput._current_mouse_pressed = moderngl_window.window()._mouse_buttons.left

    def _get_size(self):
        return moderngl_window.window().size

    def _get_ortho_projection(self):
        width, height = self._get_size()
        return moderngl_window.geometry.projection.ortho(0, width, height, 0, -1, 1)

class Windower(Enum):
    GLFW = _GLFWDriver
    MGLW = _MGLWDriver