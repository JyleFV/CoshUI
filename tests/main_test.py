from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def hovered():
    animate("scale", get_node("element3"), 1.2, 0.15, "ease_in")

def unhover():
    animate("scale", get_node("element3"), 1.0, 0.15, "ease_in")

def clicked():
    animate("position", get_node("container1"), (100, 100), 0.35, "ease_in")

def released():
    animate("position", get_node("container1"), (0, 0), 0.35, "ease_in")

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(sizing=CoshSizing.FIT, layout=CoshLayout(padding=20), gap=10):
            with Container(z_index=10, sizing=CoshSizing.FIXED, gap=12.5, id="container1", layout=CoshLayout(width=200, height=200, padding=12.5), style=CoshStyling(background_color=(255, 255, 100), border_radius=20)):
                Button(z_index=1, id="element", layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(255, 0, 0), border_radius=100))
                Button(z_index=0, id="element2", layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 255, 0)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(100, 0, 255)))
            with Grid(id="container2", layout=CoshLayout(padding=20), style=CoshStyling(background_color=(255, 255, 0), alpha=255, border_radius=(12, 12, 5, 5)), column_count=3, gap=20):
                Button(on_unhover=unhover, on_hover=hovered, on_click=clicked, on_release=released, z_index=1, id="element3", layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(255, 0, 0), border_radius=100))
                Button(z_index=0, id="element4", layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(0, 255, 0)))
                Button(layout=CoshLayout(width=50, height=50), style=CoshStyling(background_color=(100, 0, 255), border=(255, 1, 0, 2)))
                Button(id="magenta_btn", on_hover=hovered,width=50, height=50, style=CoshStyling(background_color=(255, 0, 255)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    add_class("red", CoshStyling(background_color=(0, 0, 255)))
    add_class("blue", CoshStyling(background_color=(255, 0, 0)))
    add_class("radius", CoshStyling(border_radius=5))

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