import moderngl
import moderngl_window as mglw
import coshui as cui

# NOTE: `moderngl_window` is fucking terrible when it comes to making external tooling. Because it doesn't provide a simple way to get the position
# of the mouse relative to the window, CoshUI has to reach out into the internals and poll a private member variable, more specifically the `_mouse_pos`
# variable of the current window. But here's the thing, they don't update this private variable. It only gets updates when the internal method `_calc_mouse_delta()`
# is called. Meaning, there are 2 ways to fix this, #1 the current fix in this file which overrides the `on_mouse_position_event()` method and sets `_mouse_pos`
# there, or #2 call `mglw.window()._calc_mouse_delta(self.mouse_x, self.mouse_y)` BEFORE the UI code runs. Either way, both are genuine hacks which I don't like 
# >:(

# NOTE: MGLW is still very weird, maybe I'll work on it at a later time

class MyRenderer(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL CoshUI Test"
    window_size = (800, 800)
    aspect_ratio = 16 / 9
    resizable = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse_x = 0
        self.mouse_y = 0
        self.coshui_backend = cui.ModernGLBackend(self.ctx, cui.MGLW)

    def on_render(self, time: float, frametime: float):
        self.ctx.clear(0.1, 0.1, 0.1)

        with cui.CoshUIRenderer(self.coshui_backend, cui.DEBUG):
            with cui.Container(id="main_root", width=cui.FILL, height=cui.FILL, padding=10):
                cui.Container(id="test", width=100, height=100, style=cui.CoshStyling(background_color=(255, 255, 0), border=((255, 0, 0), 5), alpha=10, border_radius=(5, 20, 5, 20)))

        if cui.get_signal("test", cui.CLICKED):
            cui.animate("transform_rotation", "test", 45.0, 1.0, "ease_out_bounce")
        if cui.get_signal("test", cui.RELEASED):
            cui.animate("transform_rotation", "test", 0.0, 1.0, "ease_out_bounce")

    def on_resize(self, width: int, height: int):
        self.ctx.viewport = (0, 0, width, height)

    def on_mouse_position_event(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

        # NOTE: This `on_mouse_position_event` function and this _mouse_pos = (x, y) is
        # necessary for CoshUI's interaction system to work. 
        mglw.window()._mouse_pos = (x, y)

if __name__ == '__main__':
    mglw.run_window_config(MyRenderer)
    