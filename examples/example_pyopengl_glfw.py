import coshui as cui
import glfw
from OpenGL.GL import *

def main():
    if not glfw.init(): return

    window = glfw.create_window(800, 800, "PyOpenGL::GLFW CoshUI Test", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    backend = cui.PyOpenGLBackend(cui.GLFW)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        with cui.CoshUIRenderer(backend, cui.DEBUG):
            with cui.Container(id="container_1", width=cui.FILL, height=cui.FILL, style=cui.CoshStyling(background_color=(80, 75, 255)), align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                with cui.Container(id="main_container", direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=15, style=cui.CoshStyling(background_color=(255, 200, 200))):
                    cui.Label(id="main_label", text="CoshUI Menu", font_size=52)
                    cui.Button(id="settings_button", text="Settings is a stupid thing to talk about and I don't like it", text_overflow=cui.TEXT_WRAP, height=50, text_justify=cui.TEXT_JUSTIFY_CENTER)
                    cui.Button(id="quit_button", text="Quit", height=50, width=150)
                    cui.Image(id="test_image", src="assets/image.png", width=75, height=75)

        if cui.get_signal("settings_button", cui.CLICKED):
            cui.animate("transform_scale", "main_label", 1.2, 0.25, "ease_in")
            cui.animate("background_color", "main_container", (255, 0, 0), 1.5, "ease_in")
        if cui.get_signal("settings_button", cui.RELEASED):
            cui.animate("transform_scale", "main_label", 1.0, 0.25, "ease_in")
            cui.animate("background_color", "main_container", (255, 200, 200), 1.5, "ease_out")

        if cui.get_signal("quit_button", cui.HOVER_ENTER):
            cui.animate("transform_rotation", "quit_button", 0.0, 0.5, "ease_out_bounce")
        if cui.get_signal("quit_button", cui.HOVER_EXIT):
            cui.animate("transform_rotation", "quit_button", 45.0, 0.5, "ease_out_bounce")

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
