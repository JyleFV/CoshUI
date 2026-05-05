from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def hovered():
    animate("scale", "cb", 1.5, 0.5, "ease_in")

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(id="new_container", classes="main_container", layout=CoshLayout(padding=20), sizing=CoshSizing.FIT, gap=10, align=CoshAlign.CENTER):
            Checkbox(id="cb", checked=True, checked_color=(255, 255, 0), on_hover=hovered)
            Button(id="btn", text="Hello")
            Label(id="lbl", text="Hello World!")
            Image(id="img", src="assets/image.png")

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

        screen.fill(BLACK)  # Clear the screen

        UI(screen)   

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(FPS)        # Ensure the loop runs at the specified FPS

    pygame.quit()

if __name__ == "__main__":
    main()