import pygame as py
import coshui as cui

WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)
counter = 0

def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    py.display.set_caption("CoshUI Test")
    clock = py.time.Clock()

    cui.add_class("label_color", cui.CoshStyling(background_color=(100, 255, 100)))

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False

        screen.fill(BLACK)

        with cui.CoshUIRenderer(cui.PygameBackend(screen)):
            with cui.Container(id="container_1", width=cui.FILL, height=cui.FILL, style=cui.CoshStyling(background_color=(80, 75, 255)), align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                with cui.Container(id="main_container", direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=15):
                    cui.Label(id="main_label", text="CoshUI Menu", font_size=52)
                    cui.Button(id="settings_button", text="Settings")
                    cui.Button(id="quit_button", text="Quit")

        if cui.get_signal("settings_button", cui.CLICKED):
            cui.animate("scale", "main_label", 1.2, 0.25, "ease_in")
        if cui.get_signal("settings_button", cui.RELEASED):
            cui.animate("scale", "main_label", 1.0, 0.25, "ease_in")

        py.display.flip()
        clock.tick(FPS)

    py.quit()

if __name__ == "__main__":
    main()