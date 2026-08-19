class CoshInput:
    _mouse_position: tuple = (0, 0)
    _prev_mouse_position: tuple = (0, 0)
    _mouse_delta: tuple = (0, 0)
    _prev_mouse_pressed: bool = False
    _current_mouse_pressed: bool = False
    _text_buffer: list = []
    _scroll_offset: tuple = (0, 0)
    # These are commented out in case we want to track left and right mouse buttons.
    # _prev_mouse_pressed_left: bool = False
    # _current_mouse_pressed_left: bool = False
    # _prev_mouse_pressed_right: bool = False
    # _current_mouse_pressed_right: bool = False

    @classmethod
    def get_mouse_just_pressed(cls) -> bool:
        return cls._current_mouse_pressed and not cls._prev_mouse_pressed
    
    @classmethod
    def get_mouse_down(cls) -> bool:
        return cls._current_mouse_pressed
    
    @classmethod
    def get_mouse_just_released(cls) -> bool:
        return cls._prev_mouse_pressed and not cls._current_mouse_pressed
    
    @classmethod
    def get_mouse_position(cls) -> tuple:
        return cls._mouse_position