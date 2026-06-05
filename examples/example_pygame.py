import pygame as py
import coshui as cui

WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)
counter = 0

def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    py.display.set_caption("Pygame CoshUI Test")
    clock = py.time.Clock()

    cui.add_class("label_color", cui.CoshStyling(background_color=(100, 255, 100)))

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False

        screen.fill(BLACK)

        with cui.CoshUIRenderer(cui.PygameBackend(screen), cui.DEBUG):
            with cui.Container(id="main_root", width=cui.FILL, height=cui.FILL, padding=10):
                cui.Container(id="test", width=100, height=100, style=cui.CoshStyling(background_color=(255, 255, 0)))

        if cui.get_signal("test", cui.CLICKED):
            cui.animate("transform_rotation", "test", 45.0, 1.0, "ease_out_bounce")
        if cui.get_signal("test", cui.RELEASED):
            cui.animate("transform_rotation", "test", 0.0, 1.0, "ease_out_bounce")
        if cui.get_signal("quit_button", cui.CLICKED):
            running = False

        py.display.flip()
        clock.tick(FPS)

    py.quit()

if __name__ == "__main__":
    main()