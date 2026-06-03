import glfw
import sys

def main():
    if not glfw.init(): return

    window = glfw.create_window(800, 800, "GLFW Window", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        # Render here
        glfw.swap_buffers(window)
        glfw.poll_events()
        
        print(glfw.get_window_size(glfw.get_current_context()))

    glfw.terminate()

if __name__ == "__main__":
    main()
