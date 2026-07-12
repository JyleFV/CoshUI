import pygame as py
import coshui as cui

WIDTH, HEIGHT = 700, 700
FPS = 60
BLACK = (0, 0, 0)

def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    py.display.set_caption("Pygame CoshUI Test")
    clock = py.time.Clock()

    cui.add_class("label_color", cui.CoshStyling(background_color=(100, 255, 100)))

    itemList = ["Hello", "World", "My", "Name"]

    running = True
    while running:
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False

        screen.fill(BLACK)

        with cui.CoshUIRenderer(cui.PygameBackend(screen)):
            with cui.Container(id="container_1", width=cui.FILL, height=cui.FILL, style=cui.CoshStyling(background_color=(80, 75, 255)), align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                with cui.Container(id="main_container", mouse_filter=cui.STOP, direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=15, style=cui.CoshStyling(background_color=(255, 200, 200))):
                    cui.Label(id="main_label", text="CoshUI Menu", font_size=52, text_overflow=cui.TEXT_HIDDEN)
                    cui.Button(id="settings_button", text="Settings", height=50, text_justify=cui.TEXT_JUSTIFY_CENTER)
                    cui.Button(id="quit_button", text="Quit", height=50, width=150)
                    cui.Image(id="test_image", src="assets/image.png", width=75, height=75)
                    cui.Dropdown(id="dropdown", item_list=itemList)
                    cui.Slider(id="slider", width=100)
                    cui.Checkbox(id="checkbox")

        if cui.get_signal("settings_button", cui.CLICKED):
            cui.animate("transform_scale", "main_label", 1.2, 0.25, "ease_in")
            cui.animate("background_color", "main_container", (255, 0, 0), 1.5, "ease_in")
        if cui.get_signal("settings_button", cui.RELEASED):
            cui.animate("transform_scale", "main_label", 1.0, 0.25, "ease_in")
            cui.animate("background_color", "main_container", (255, 200, 200), 1.5, "ease_out")

        if cui.get_signal("quit_button", cui.HOVER_ENTER):
            cui.animate("transform_rotation", "test_image", 0.0, 0.5)
        if cui.get_signal("quit_button", cui.HOVER_EXIT):
            cui.animate("transform_rotation", "test_image", 45.0, 0.5)
        if cui.get_signal("quit_button", cui.CLICKED):
            running = False

        py.display.flip()
        clock.tick(FPS)

    py.quit()

if __name__ == "__main__":
    main()