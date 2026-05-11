from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)

is_checked = Ref(False)
vol = Ref(50.0)
brightness = Ref(75.0)
settings_open = False

def main():
    global settings_open
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    add_class("card", CoshStyling(background_color=(50, 50, 70), border_radius=20, border=((255, 255, 255), 2)))
    add_class("btn_primary", CoshStyling(background_color=(100, 80, 220), border_radius=10))
    add_class("btn_danger", CoshStyling(background_color=(180, 60, 60), border_radius=10))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="root", sizing=FILL, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, style=CoshStyling(background_color=(30, 28, 80))):
                with Container(id="main_col", direction=CoshDirection.COLUMN, gap=16, align=CoshAlign.CENTER):
                    Label(id="title", text="My App", font_size=52)
                    Button(id="play_btn", text="Play", classes="btn_primary", width=200)
                    Button(id="settings_btn", text="Settings", width=200)
                    Button(id="quit_btn", text="Quit", classes="btn_danger", width=200)
                with Modal(id="modal", width=400, height=300, z_index=10, padding=20):
                    Label(id="modal_lbl", text="Hello from Modal!", font_size=24)
                    Button(id="modal_btn", text="Click Me")

                if settings_open:
                    with Container(id="overlay", align=CoshAlign.CENTER, justify=CoshJustify.CENTER, style=CoshStyling(), positioning=CoshPositioning.ABSOLUTE, z_index=10):
                        with Container(id="settings_card", direction=CoshDirection.COLUMN, gap=30, align=CoshAlign.CENTER, classes="card", padding=30, z_index=11):
                            Label(id="settings_title", text="Settings", font_size=32)
                            with Container(id="row_sfx", gap=20, align=CoshAlign.CENTER):
                                Label(id="lbl_sfx", text="SFX", font_size=20)
                                Checkbox(id="cb_sfx", checked=is_checked.value, bind=is_checked, z_index=12)
                            with Container(id="row_vol", gap=20, align=CoshAlign.CENTER):
                                Label(id="lbl_vol", text=f"Volume: {int(vol.value)}", font_size=20)
                                Slider(id="sldr_vol", width=200, bind=vol, min_value=0, max_value=100, z_index=12)
                            with Container(id="row_brightness", gap=20, align=CoshAlign.CENTER):
                                Label(id="lbl_brightness", text=f"Brightness: {int(brightness.value)}", font_size=20)
                                Slider(id="sldr_brightness", width=200, bind=brightness, min_value=0, max_value=100, z_index=12)
                            Button(id="close_btn", text="Close", classes="btn_danger", width=150, z_index=12)

        if get_signal("settings_btn", "clicked") or get_signal("close_btn", "clicked"):
            settings_open = not settings_open

        if get_signal("quit_btn", "clicked"):
            running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()