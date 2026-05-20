import raylibpy as rl
import coshui as cui

WIDTH, HEIGHT = 800, 800
FPS = 60

def main():
    rl.init_window(WIDTH, HEIGHT, "Raylib CoshUI Test")
    rl.set_target_fps(FPS)

    print((rl.get_screen_width(), rl.get_screen_height()))

    cui.add_class("label_color", cui.CoshStyling(background_color=(100, 255, 100)))

    while not rl.window_should_close():
        rl.clear_background(rl.BLACK)
        rl.begin_drawing()
        
        with cui.CoshUIRenderer(cui.RaylibBackend()):
            with cui.Container(id="container_1", width=cui.FILL, height=cui.FILL, style=cui.CoshStyling(background_color=(80, 75, 255)), align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                with cui.Container(id="main_container", direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=15):
                    cui.Label(id="main_label", text="CoshUI Menu", font_size=52)
                    cui.Button(id="settings_button", text="Settings")
                    cui.Button(id="quit_button", text="Quit")
        
        rl.end_drawing()

        if cui.get_signal("settings_button", cui.CLICKED):
            cui.animate("scale", "main_label", 1.2, 0.25, "ease_in")
        if cui.get_signal("settings_button", cui.RELEASED):
            cui.animate("scale", "main_label", 1.0, 0.25, "ease_in")

        if cui.get_signal("quit_button", cui.CLICKED):
            rl.close_window()

    rl.close_window()

if __name__ == "__main__":
    main()
