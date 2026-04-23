from coshui import *
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("My Pygame Window")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(BLACK)  # Clear the screen

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(layout=CoshLayout(width=200, height=200), style=CoshStyling(background_color=Vector4(255, 255, 100, 1))):
                pass

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(FPS)        # Ensure the loop runs at the specified FPS

    pygame.quit()

if __name__ == "__main__":
    main()