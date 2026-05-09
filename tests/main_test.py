from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
is_checked = Ref(False)
state = True
vol = Ref(0.0)

def main():
    global state
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    add_class("main_container", CoshStyling(background_color=(200, 100, 0)))
    add_class("button_primary", CoshStyling(background_color=(200, 100, 255), border_radius=20))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)  # Clear the screen

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="container_1", sizing=CoshSizing.FILL, layout=CoshLayout(padding=20), style=CoshStyling(background_color=(80, 75, 255)), align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
                with Container(id="container_2", classes="main_container", direction=CoshDirection.COLUMN, gap=10, align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
                    Label(id="lbl", text="CoshUI", width=100, height=100, font_size=64)
                    Button(id="start_btn", text="Start", classes="button_primary")
                    Button(id="settings_btn", text="Settings", classes="button_primary")
                    Button(id="quit_btn", text="Quit")
                    Checkbox(id="cb", bind=is_checked)
                    Slider(id="sldr", width=200, bind=vol, min_value=50, max_value=100)
                    # with Container(id="container_3", mouse_filter=CoshMouseFilter.STOP, style=CoshStyling(background_color=(255, 100, 100)), x=WIDTH/2, y=HEIGHT/2, positioning=CoshPositioning.ABSOLUTE, layout=CoshLayout(padding=20)):
                    #     Button(id="hello", text="Click Me")

        print(vol.value)

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(FPS)        # Ensure the loop runs at the specified FPS

    pygame.quit()

if __name__ == "__main__":
    main()