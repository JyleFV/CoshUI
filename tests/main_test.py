from coshui import *
from coshui.engine import CoshUI
import pygame

WIDTH, HEIGHT = 1200, 900
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(sizing=CoshSizing.FIT, layout=CoshLayout(padding=20), gap=10):
            with Container(sizing=CoshSizing.FIXED, gap=12.5, id="container1", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=(255, 255, 100, 255), border_radius=20)):
                Button(id="element", layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(255, 0, 0, 100), border_radius=100))
                Button(id="element2", layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 255, 0, 20)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(100, 0, 255)))
            with Container(direction=CoshDirection.COLUMN,sizing=CoshSizing.FIXED, gap=12.5, id="container2", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=(255, 255, 100, 255))):
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(255, 0, 0)))    
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 255, 100)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 0, 255)))
            with Container(sizing=CoshSizing.FIXED, gap=12.5, id="container3", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=(255, 255, 100, 255))):
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(255, 100, 0)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 255, 0)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 0, 255)))

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