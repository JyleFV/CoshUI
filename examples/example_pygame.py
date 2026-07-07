from abc import ABC, abstractmethod

import pygame as py
import coshui as cui

WIDTH, HEIGHT = 800, 800

class Entity(ABC):
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = color

    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def update(self):
        pass

class Player(Entity):
    def __init__(self, x, y, w, h, color):
        super().__init__(x, y, w, h, color)
        self.speed = 5
        self.health = 100

    def draw(self, screen):
        py.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self):
        keys = py.key.get_pressed()
        if keys[py.K_a]:
            self.x -= self.speed
        if keys[py.K_d]:
            self.x += self.speed
        if keys[py.K_w]:
            self.y -= self.speed
        if keys[py.K_s]:
            self.y += self.speed

class Game():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = py.display.set_mode((self.width, self.height))
        py.display.set_caption("Two Rectangles - Pygame")

        self.clock = py.time.Clock()
        self.running = True
        
        # 1. Player starts at (0, 0)
        self.player = Player(0, 0, 50, 50, (0, 120, 255)) # Blue player
        
        # 2. Static Red Rectangle in the middle (50x50)
        center_x = (self.width // 2) - 25
        center_y = (self.height // 2) - 25
        self.center_rect = py.Rect(center_x, center_y, 50, 50)

        cui.add_class("example", cui.CoshStyling(background_color=(255, 100, 100)))
        cui.add_class("border", cui.CoshStyling(border=((0, 0, 255), 5)))
    
    def run(self):
        while self.running:
            for event in py.event.get():
                if event.type == py.QUIT:
                    self.running = False
            
            self.update()
            
            # Rendering
            self.screen.fill((30, 30, 30)) 

            # Draw the static red rectangle in the middle
            py.draw.rect(self.screen, (255, 0, 0), self.center_rect)
            
            # Draw the player
            self.player.draw(self.screen)
            
            with cui.CoshUIRenderer(cui.PygameBackend(self.screen), cui.DEBUG):
                with cui.Container(id="root", padding=10):
                    with cui.Container(id="health_container", width=400, height=25, padding=10, style=cui.CoshStyling(background_color=(50, 50, 50), border_radius=20)):
                        with cui.Container(id="health_bar", width=max(0, self.player.health * 3.8), height=cui.FILL, style=cui.CoshStyling(background_color=(100, 255, 100), border_radius=20)):
                            pass
                if self.player.health <= 0:
                    with cui.Container(id="second_root", width=WIDTH, height=HEIGHT, positioning=cui.ABSOLUTE, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, style=cui.CoshStyling(background_color=(0, 0, 0), alpha=0)):
                        with cui.Container(id="dead_container", direction=cui.COLUMN, align=cui.ALIGN_CENTER, justify=cui.JUSTIFY_CENTER, gap=20):
                            cui.RichLabel(id="title", text="[red font_size=48]You Died![/][blue] Haha[/]")
                            cui.Button(id="restart_btn", text="Restart")
                            cui.Button(id="quit_btn", text="Quit")
                
            if self.player.health <= 0:
                if self.player.health <= 0:
                    cui.animate("alpha", "second_root", 255, 1.5, "ease_in")

                if cui.get_signal("quit_btn", cui.CLICKED):
                    self.running = False
            
                if cui.get_signal("restart_btn", cui.CLICKED):
                    self.player.x, self.player.y = 0, 0
                    self.player.health = 100

            py.display.flip()
            self.clock.tick(60)
            
        py.quit()

    def update(self):
        self.player.update()
        
        # Rect representation of the player
        player_rect = py.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        # Check if the player's rect collides with the center cube
        if player_rect.colliderect(self.center_rect):
            # Lower health (e.g., reduce by 1 per frame or use a timer)
            self.player.health = max(0, self.player.health - 1)

def main():
    py.init()
    game = Game(WIDTH, HEIGHT)
    game.run() # Handles the loop internally and exits cleanly

if __name__ == "__main__":
    main()