from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
paused = False

def hovered():
    animate("alpha", "img", 100, 0.5, "ease_in")

def UI(screen : pygame.Surface):
    with CoshUIRenderer(PygameBackend(screen)):
        with Container(id="new_container", classes="main_container", layout=CoshLayout(padding=20), sizing=CoshSizing.FIT, gap=10, align=CoshAlign.CENTER):
            if paused:
                Button(id="pause", text="Hello Paused")
            Checkbox(id="cb", checked=True, checked_color=(255, 255, 0), on_hover=hovered)
            Button(text="Click Me")
            Label(id="lbl", text="Hello World!", text_color=(255, 100, 100))
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    global paused
                    paused = not paused

        screen.fill(BLACK)  # Clear the screen

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="container_1", sizing=CoshSizing.FILL, layout=CoshLayout(padding=20), style=CoshStyling(background_color=(80, 75, 255)), align=CoshAlign.CENTER, justify=CoshJustify.CENTER):
                with Container(id="container_2", direction=CoshDirection.COLUMN, gap=10, align=CoshAlign.CENTER):
                    Label(id="lbl", text="CoshUI", width=500, height=100, font_size=32)
                    Button(id="start_btn", text="Start")
                    Button(id="settings_btn", text="Settings")
                    Button(id="quit_btn", text="Quit")

        pygame.display.flip()  # Update the full display Surface to the screen
        clock.tick(FPS)        # Ensure the loop runs at the specified FPS

    pygame.quit()

if __name__ == "__main__":
    main()