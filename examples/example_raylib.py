import raylibpy as rl
import coshui as cui

WIDTH, HEIGHT = 800, 800
FPS = 60

def main():
    rl.init_window(WIDTH, HEIGHT, "Raylib CoshUI Test")
    rl.set_target_fps(FPS)

    cui.add_class("label_color", cui.CoshStyling(background_color=(100, 255, 100)))

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        
        with cui.CoshUIRenderer(cui.RaylibBackend()):
            with cui.Container(id="main_root", width=cui.FILL, height=cui.FILL, padding=10, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER):
                cui.Container(id="test", width=100, height=100, style=cui.CoshStyling(background_color=(255, 255, 0), border=((255, 100, 100), 10), border_radius=(20, 20, 0, 0)))

        rl.end_drawing()

        if cui.get_signal("test", cui.CLICKED):
            cui.animate("transform_rotation", "test", 45.0, 1.0, "ease_out_bounce")
        if cui.get_signal("test", cui.RELEASED):
            cui.animate("transform_rotation", "test", 0.0, 1.0, "ease_out_bounce")

        if cui.get_signal("quit_button", cui.RELEASED):
            break;

    rl.close_window()

if __name__ == "__main__":
    main()
