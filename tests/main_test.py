from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def clicked():
    animate("scale", get_node("element"), 1.5, 0.1, "linear")

def released():
    animate("scale", get_node("element"), 1.0, 0.1, "linear")

def hovered():
    animate("scale", get_node("logo"), 0.8, 0.15, "ease_in")

def unhovered():
    animate("scale", get_node("logo"), 1.0, 0.15, "ease_in")

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        # with Container(sizing=CoshSizing.FIT, gap=10, justify=CoshJustify.CENTER, align=CoshAlign.CENTER):
        #     with Container(direction=CoshDirection.ROW, sizing=CoshSizing.FILL, width=500, height=500, gap=20, style=CoshStyling(background_color=(50, 255, 50)), layout=CoshLayout(padding=20)):
        #         Button(id="element", width=50, height=65, style=CoshStyling(background_color=(255, 50, 50)), sizing=CoshSizing.FILL)
        #         with Container(id="hello", justify=CoshJustify.END, align=CoshAlign.END, sizing=CoshSizing.FILL, style=CoshStyling(background_color=(255, 50, 255))):
        #             Button(on_unhover=unhovered, on_hover=hovered, on_click=clicked, on_release=released, id="yellow_btn", width=50, height=50, style=CoshStyling(background_color=(255, 255, 0)))
        #             Button(text="Hello", classes="main_btn")
        with Container(classes="main_container", layout=CoshLayout(padding=20), sizing=CoshSizing.FIT, gap=10, align=CoshAlign.CENTER):
            # Label(text="Hello!")
            # Button(sizing=CoshSizing.FIT, text="FUCK YOU")
            # Button(text="Hello")
            # Image(id="logo", on_unhover=unhovered, on_hover=hovered,src="assets/image.png", sizing=CoshSizing.FILL, style=CoshStyling(alpha=100))
            Checkbox(id="cb")
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