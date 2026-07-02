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
            with cui.Container(id="root_container", width=cui.FILL, height=cui.FILL, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, style=cui.CoshStyling(background_color=(100, 100, 255))):
                cui.RichLabel(id="first_rich", 
                            text="[red font=Ubuntu font_size=52]Hello[/] [color=(100, 100, 255)]World! My name is JyleFV and I really[/] like Minecraft!", 
                            text_color=(0, 0, 0), text_align=cui.TEXT_ALIGN_TOP, text_justify=cui.TEXT_JUSTIFY_CENTER, width=200, height=200, text_overflow=cui.TEXT_WRAP, 
                            style=cui.CoshStyling(background_color=(255, 255, 255))
                )

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
