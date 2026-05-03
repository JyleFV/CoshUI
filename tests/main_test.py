from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def hovered():
    animate("position", get_node("element"), (200, 0), 0.35, "ease_in")

def unhovered():
    animate("position", get_node("element"), (0, 0), 0.35, "ease_in_out")

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(sizing=CoshSizing.FIT, gap=10, justify=CoshJustify.CENTER, align=CoshAlign.CENTER):
            with Container(direction=CoshDirection.ROW, sizing=CoshSizing.FILL, width=500, height=500, gap=20, style=CoshStyling(background_color=(50, 255, 50)), layout=CoshLayout(padding=20)):
                Button(id="element", width=50, height=65, style=CoshStyling(background_color=(255, 50, 50)), sizing=CoshSizing.FILL, z_index=1)
                with Container(justify=CoshJustify.END, align=CoshAlign.END, sizing=CoshSizing.FILL, style=CoshStyling(background_color=(255, 50, 255))):
                    Button(id="hello", z_index=10, on_hover=hovered, on_unhover=unhovered, width=50, height=50, style=CoshStyling(background_color=(255, 255, 0)), layout=CoshLayout(margin=20))

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