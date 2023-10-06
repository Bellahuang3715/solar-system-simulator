import pygame
import math

# pygame.init()

WHITE = (255, 255, 255)
FONT = pygame.font.SysFont("comicsans", 16)

class Planet:

    AU = 149.6e6 * 1000                 # astronomical units
    G = 6.67428e-11                     # force of attraction between objects
    SCALE = 250 / AU                    # 1AU = 100 pixels
    TIMESTEP = 3600 * 24                # 1 day

    def __init__(self, name, image, x, y, radius, colour, mass):
        self.name = name
        self.image = image
        self.x = x
        self.y = y
        self.colour = colour
        self.radius = radius
        self.mass = mass

        self.x_velocity = 0
        self.y_velocity = 0

        self.sun = False
        self.distance_to_sun = 0
        self.orbit = []             # points planet has travelled around


    def draw(self, window, width, height, offset_x, offset_y, zoom_level):
        x = (self.x * self.SCALE + width / 2 - offset_x) * zoom_level
        y = (self.y * self.SCALE + height / 2 - offset_y) * zoom_level

        if len(self.orbit) > 2:

            updated_points = []
            for point in self.orbit:
                x, y = point
                x = (x * self.SCALE + width / 2 - offset_x) * zoom_level
                y = (y * self.SCALE + height / 2 - offset_y) * zoom_level
                updated_points.append((x, y))

            pygame.draw.lines(window, self.colour, False, updated_points, int(2 * zoom_level))

        x_pos = x - self.image.get_width() // 2
        y_pos = y - self.image.get_height() // 2
        window.blit(self.image, (x_pos, y_pos))

        if not self.sun:
            distance_text = FONT.render(self.name, 1, self.colour)
            window.blit(distance_text, (x - distance_text.get_width()/2, 25 + y - distance_text.get_height()/2))


    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance ** 2
        theta=  math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y
    

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_velocity += total_fx / self.mass * self.TIMESTEP # F = ma => a = F/m
        self.y_velocity += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_velocity * self.TIMESTEP
        self.y += self.y_velocity * self.TIMESTEP
        self.orbit.append((self.x, self.y))
