import moderngl_window as mglw
import coshui as cui

# NOTE: `moderngl_window` is fucking terrible when it comes to making external tooling. Because it doesn't provide a simple way to get the position
# of the mouse relative to the window, CoshUI has to reach out into the internals and poll a private member variable, more specifically the `_mouse_pos`
# variable of the current window. But here's the thing, they don't update this private variable. It only gets updates when the internal method `_calc_mouse_delta()`
# is called. Meaning, there are 2 ways to fix this, #1 the current fix in this file which overrides the `on_mouse_position_event()` method and sets `_mouse_pos`
# there, or #2 call `mglw.window()._calc_mouse_delta(self.mouse_x, self.mouse_y)` BEFORE the UI code runs. Either way, both are genuine hacks which I don't like 
# >:(

# NOTE: MGLW is so very weird, it's not very good with external tooling so beware of using CoshUI's debugger.

class MyRenderer(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL::MGLW CoshUI Test"
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

        with cui.CoshUIRenderer(self.coshui_backend):
            with cui.Container(id="container_1", width=cui.FILL, height=cui.FILL, style=cui.CoshStyling(background_color=(80, 75, 255)), align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                with cui.Container(id="main_container", direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=15, style=cui.CoshStyling(background_color=(255, 200, 200))):
                    cui.Label(id="main_label", text="CoshUI Menu", font_size=52)
                    cui.Button(id="settings_button", text="Settings is a stupid thing to talk about and I don't like it", text_overflow=cui.TEXT_WRAP, height=50, text_justify=cui.TEXT_JUSTIFY_CENTER)
                    cui.Button(id="quit_button", text="Quit", height=50, width=150, style=cui.CoshStyling(transform_rotation=45.0))
                    cui.Image(id="test_image", src="assets/image.png", width=75, height=75, style=cui.CoshStyling(transform_rotation=45.0))

        if cui.get_signal("settings_button", cui.CLICKED):
            cui.animate("transform_scale", "main_label", 1.2, 0.25, "ease_in")
            cui.animate("background_color", "main_container", (255, 0, 0), 1.5, "ease_in")
        if cui.get_signal("settings_button", cui.RELEASED):
            cui.animate("transform_scale", "main_label", 1.0, 0.25, "ease_in")
            cui.animate("background_color", "main_container", (255, 200, 200), 1.5, "ease_out")

        if cui.get_signal("quit_button", cui.HOVERED):
            cui.animate("transform_rotation", "quit_button", 0.0, 0.5, "ease_in")
        if cui.get_signal("quit_button", cui.HOVER_EXIT):
            cui.animate("transform_rotation", "quit_button", 45.0, 0.5, "ease_in")

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
    