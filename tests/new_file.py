from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)

def main():
    global settings_open
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        
        # with CoshUIRenderer(PygameBackend(screen)):
            # with Container(id="main_containter", width=500, height=500, layout=CoshLayout(width=100, height=100), style=CoshStyling(background_color=(255, 100, 100))):
            #     pass
            # with Container(id="container_1", sizing=CoshSizing.FILL, layout=CoshLayout(padding=20), style=CoshStyling(background_color=(80, 75, 255)), align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
            #     with Container(id="container_2", direction=CoshDirection.COLUMN, gap=10, align=CoshAlign.CENTER):
            #         Label(id="label", text="CoshUI", width=100, height=100, font_size=64)
            #         Button(id="start_btn", text="Start")
            #         Button(id="settings_btn", text="Settings")
            #         Button(id="quit_btn", text="Quit")

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="root", sizing=CoshSizing.FILL, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, style=CoshStyling(background_color=(30, 28, 80))):
                Label(id="title", text="My App", font_size=52)
                with Modal(id="modal", z_index=10, direction=CoshDirection.COLUMN, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, gap=20, style=CoshStyling(alpha=100)):
                    Label(id="modal_lbl", text="Hello from Modal!", font_size=24)
                    Button(id="modal_btn", text="Click Me")
                    Slider(id="modal_slider", width=100, z_index=11)
        
        # if get_signal("modal_btn", "clicked"):
        #     animate("scale", "modal::content", 1.2, 0.5, "ease_in")
        
        # if get_signal("modal_btn", "released"):
        #     animate("scale", "modal::content", 1.0, 0.5, "ease_in")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()