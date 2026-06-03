import moderngl
import moderngl_window as mglw

class MyRenderer(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL CoshUI Test"
    window_size = (1200, 800)
    aspect_ratio = 16 / 9
    resizable = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mouse_x = 0
        self.mouse_y = 0
        # Initialization logic (load shaders, buffers, VAOs)
        # Example:
        # self.prog = self.ctx.program(...)
        
    def on_render(self, time: float, frametime: float):
        # This is your main loop, called every frame
        print(mglw.window()._mouse_pos)

        self.ctx.clear(0.1, 0.1, 0.1)  # Clear screen with dark gray
        
        # Rendering logic here
        # Example:
        # self.vao.render()

    def on_resize(self, width: int, height: int):
        # Handle window resizing if needed
        self.ctx.viewport = (0, 0, width, height)

    def on_mouse_position_event(self, x, y, dx, dy):
        # This fires whenever the mouse moves
        self.mouse_x = x
        self.mouse_y = y

if __name__ == '__main__':
    mglw.run_window_config(MyRenderer)
    