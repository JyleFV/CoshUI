from coshui import *
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(sizing=CoshSizing.FIXED, id="new_container", layout=CoshLayout(
            width=200, 
            height=200,
            padding=20
        ),     
        style=CoshStyling(
            background_color=Vector4(255, 255, 100, 100)
        )):
            with Container(sizing=CoshSizing.FIXED, id="other_container", layout=CoshLayout(width=100, height=100), style=CoshStyling(background_color=Vector4(255, 100, 100, 0.1))):
                pass

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

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