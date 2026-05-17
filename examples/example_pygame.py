from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)
counter = 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    add_class("label_color", CoshStyling(background_color=(100, 255, 100)))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="container_1", width=FILL, height=FILL, style=CoshStyling(background_color=(80, 75, 255)), align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
                with Container(id="main_container", direction=CoshDirection.COLUMN, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, gap=15):
                    Label(id="main_label", text="CoshUI Menu", font_size=48)
                    Button(id="settings_button", text="Settings")
                    Button(id="quit_button", text="Quit")

        if get_signal("main_container", CLICKED):
            animate("background_color", "new_container", (100, 100, 100), 1.5, "ease_in")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()