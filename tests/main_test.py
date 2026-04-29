from coshui import *
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(sizing=CoshSizing.FIT, layout=CoshLayout(padding=20), gap=10):
            with Container(sizing=CoshSizing.FIXED, gap=12.5, id="container1", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=Vector4(255, 255, 100, 100))):
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(255, 0, 0, 255)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(0, 255, 0, 255)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(100, 0, 255, 255)))
            with Container(sizing=CoshSizing.FIXED, gap=12.5, id="container2", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=Vector4(255, 255, 100, 100))):
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(255, 0, 0, 255)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(0, 255, 100, 255)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(0, 0, 255, 255)))
            with Container(sizing=CoshSizing.FIXED, gap=12.5, id="container3", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=Vector4(255, 255, 100, 100))):
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(255, 100, 0, 255)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(0, 255, 0, 255)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=Vector4(0, 0, 255, 255)))

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