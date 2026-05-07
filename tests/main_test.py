from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
paused = False

def hovered():
    animate("background_color", "container_3", (100, 100, 255), 0.5, "ease_in")

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    add_class("main_container", CoshStyling(background_color=(200, 100, 0)))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    global paused
                    paused = not paused

        screen.fill(BLACK)  # Clear the screen

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="container_1", sizing=CoshSizing.FILL, layout=CoshLayout(padding=20), style=CoshStyling(background_color=(80, 75, 255)), align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
                with Container(id="container_2", sizing=CoshSizing.FIT, direction=CoshDirection.COLUMN, gap=10, align=CoshAlign.CENTER):
                    Label(id="lbl", text="CoshUI", width=100, height=100, font_size=64)
                    Button(id="start_btn", text="Start")
                    Button(id="settings_btn", text="Settings")
                    Button(id="quit_btn", text="Quit")
                with Container(id="container_3", mouse_filter=False, on_hover=hovered, style=CoshStyling(background_color=(255, 100, 100)), x=WIDTH/2, y=HEIGHT/2, positioning=CoshPositioning.ABSOLUTE, layout=CoshLayout(padding=20)):
                    Button(id="hello", text="Click Me")

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(FPS)        # Ensure the loop runs at the specified FPS

    pygame.quit()

if __name__ == "__main__":
    main()