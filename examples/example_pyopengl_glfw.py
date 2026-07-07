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
            cui.RichLabel(id="first_rich", text="[red font=Ubuntu font_size=52 bold italic strikethrough underline]Hello[/][color=(255, 100, 255)] World! My name is JyleFV and I really[/] like Minecraft!", text_color=(0, 0, 0), text_align=cui.TEXT_ALIGN_TOP, text_justify=cui.TEXT_JUSTIFY_LEFT, width=200, height=500, text_overflow=cui.TEXT_WRAP, style=cui.CoshStyling(background_color=(255, 255, 255)))
            with cui.Container(id="container_1", width=cui.FILL, height=cui.FILL, style=cui.CoshStyling(background_color=(80, 75, 255)), align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                with cui.Container(id="main_container", direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=30, style=cui.CoshStyling(background_color=(255, 200, 200))):
                    cui.Label(id="main_label", bold=True, italic=True, text="CoshUI Menu", font_size=52, style=cui.CoshStyling(background_color=(255, 100, 100)))
                    cui.Button(id="settings_button", text="Settings is a stupid thing to talk about and I don't like it", text_overflow=cui.TEXT_WRAP, height=50, text_justify=cui.TEXT_JUSTIFY_CENTER)
                    cui.Button(id="quit_button", text="Quit", height=50, width=150, style=cui.CoshStyling(transform_rotation=45.0))
                    cui.Image(id="test_image", src="assets/image.png", width=75, height=75, style=cui.CoshStyling(transform_rotation=45.0))

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
