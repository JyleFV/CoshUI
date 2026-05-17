import raylibpy as rl
from coshui import *

WIDTH, HEIGHT = 800, 800
FPS = 60

def main():
    rl.init_window(WIDTH, HEIGHT, "CoshUI Test")
    rl.set_target_fps(FPS)

    print((rl.get_screen_width(), rl.get_screen_height()))

    add_class("label_color", CoshStyling(background_color=(100, 255, 100)))

    while not rl.window_should_close():
        rl.clear_background(rl.BLACK)
        rl.begin_drawing()
        
        with CoshUIRenderer(RaylibBackend()):
            with Container(id="container_1", width=FILL, height=FILL, style=CoshStyling(background_color=(80, 75, 255)), align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
                with Container(id="main_container", direction=CoshDirection.COLUMN, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, gap=15):
                    Label(id="main_label", text="CoshUI Menu", font_size=48)
                    Button(id="settings_button", text="Settings")
                    Button(id="quit_button", text="Quit")
        
        rl.end_drawing()

        if get_signal("root3", CLICKED):
            animate("background_color", "root", (100, 100, 100), 1.5, "ease_in")

    rl.close_window()

if __name__ == "__main__":
    main()
