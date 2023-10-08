import pygame
import random

class Star:

    x: float
    y: float
    brightness: int

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.brightness = random.randint(10, 255)

    def update(self):
        self.brightness += random.randint(-20, 20)
        self.brightness = max(10, min(255, self.brightness))

    def draw(self, window):
        star_surface = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.circle(star_surface, (255, 255, 255, self.brightness), (2, 2), 2)
        window.blit(star_surface, (self.x, self.y))
