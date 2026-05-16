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

    add_class("label_color", CoshStyling(background_color=(100, 255, 100)))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        with CoshUIRenderer(PygameBackend(screen)):
            with Container(id="root", direction=CoshDirection.ROW, style=CoshStyling(background_color=(100, 100, 255)), padding=10, gap=10):
                # with Container(id="root2", width=50, style=CoshStyling(background_color=(255, 100, 100))):
                #     pass
                with Container(id="root3", width=750, style=CoshStyling(background_color=(255, 100, 100)), justify=CoshJustify.SPACE_AROUND, gap=10, padding=10):
                    Label(id="lbl", text="Hello", classes="label_color")
                    Label(id="lbl1", text="Hello", classes="label_color")
                    Label(id="lbl2", text="Hello", classes="label_color")
                    Label(id="lbl3", text="Hello", classes="label_color")
                # with Grid(id="grid_root", column_count=2, width=500, height=500, style=CoshStyling(background_color=(255, 200, 200)), gap=10, padding=20):
                #     # with Container(id="root4", style=CoshStyling(background_color=(255, 200, 100)), positioning=CoshPositioning.ABSOLUTE): # TODO: Fix absoulute bug
                #     #     pass
                #     with Container(id="root5", style=CoshStyling(background_color=(255, 100, 100))):
                #         pass
                #     with Container(id="root6", style=CoshStyling(background_color=(255, 100, 100))):
                #         pass
                #     with Container(id="root7", style=CoshStyling(background_color=(255, 100, 100))):
                #         pass
                #     with Container(id="root8", style=CoshStyling(background_color=(255, 100, 100))):
                #         pass

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()