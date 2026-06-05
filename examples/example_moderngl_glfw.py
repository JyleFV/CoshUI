import coshui as cui
import moderngl
import glfw

def main():
    if not glfw.init(): return

    window = glfw.create_window(800, 800, "ModernGL::GLFW CoshUI Test", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    ctx = moderngl.create_context()
    # Better to create the backend once so shader compilation and all that is only done once.
    backend = cui.ModernGLBackend(ctx, cui.GLFW)

    while not glfw.window_should_close(window):
        # Render here
        ctx.clear(0.1, 0.1, 0.1, 1.0)

        with cui.CoshUIRenderer(backend, cui.DEBUG):
            with cui.Container(id="main_root", width=cui.FILL, height=cui.FILL, padding=10):
                cui.Container(id="test", width=100, height=100, style=cui.CoshStyling(background_color=(255, 255, 0), alpha=10, border_radius=20))

        if cui.get_signal("test", cui.CLICKED):
            cui.animate("transform_rotation", "test", 45.0, 1.0, "ease_out_bounce")
        if cui.get_signal("test", cui.RELEASED):
            cui.animate("transform_rotation", "test", 0.0, 1.0, "ease_out_bounce")

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
