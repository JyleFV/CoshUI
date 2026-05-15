from coshui import *
import pygame

WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)
counter = 0

def main():
    global counter
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CoshUI Test")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="root", sizing=FILL, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, style=CoshStyling(background_color=(30, 28, 80))):
                Label(id="title", text="My App", font_size=52)
                with Container(id="test", padding=10):
                    Label(id="test2", text="Test!", width=100)
                with Modal(id="modal", z_index=10, direction=CoshDirection.COLUMN, align=CoshAlign.CENTER, justify=CoshJustify.CENTER, gap=20):
                    Label(id="modal_lbl", text="Hello from Modal!", font_size=24)
                    Button(id="modal_btn", text="Click Me")
                    Slider(id="modal_slider", width=100, z_index=11)
                    Checkbox(id="cb")

        if get_signal("modal_btn", CLICKED):
            counter += 1
            print(f"hello world! counter: {counter}")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()