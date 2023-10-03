import pygame 
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
WIND = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulator")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 80)
LIGHT_GREY = (211, 211, 211)

# ------------------------ #
zoom_level = 1.0
offset_x = 0
offset_y = 0

ZOOM_IN_BUTTON = pygame.Rect(10, 10, 50, 50)
ZOOM_OUT_BUTTON = pygame.Rect(70, 10, 50, 50)
BUTTON_FONT = pygame.font.Font(None, 40)

ZOOM_IN_TEXT = BUTTON_FONT.render("+", True, BLACK)
ZOOM_OUT_TEXT = BUTTON_FONT.render("-", True, BLACK)

# ------------------------ #


FONT = pygame.font.SysFont("comicsans", 16)

class Planet:

    AU = 149.6e6 * 1000                 # astronomical units
    G = 6.67428e-11                     # force of attraction between objects
    SCALE = 250 / AU                    # 1AU = 100 pixels
    TIMESTEP = 3600 * 24               # 1 day

    def __init__(self, x, y, radius, colour, mass):
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


    def draw(self, window):
        x = (self.x * self.SCALE + WIDTH / 2 - offset_x) * zoom_level
        y = (self.y * self.SCALE + HEIGHT / 2 - offset_y) * zoom_level
        radius = self.radius * zoom_level

        if len(self.orbit) > 2:

            updated_points = []
            for point in self.orbit:
                x, y = point
                x = (x * self.SCALE + WIDTH / 2 - offset_x) * zoom_level
                y = (y * self.SCALE + HEIGHT / 2 - offset_y) * zoom_level
                updated_points.append((x, y))

            pygame.draw.lines(window, self.colour, False, updated_points, int(2 * zoom_level))

        pygame.draw.circle(window, self.colour, (x, y), radius)

        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)}km", 1, WHITE)
            window.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))


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


def config_planets():
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10 **30) # in kg
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10 **24)
    earth.y_velocity = 29.783 * 1000 # m/s

    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.39 * 10**23)
    mars.y_velocity = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 3.30 * 10**23)
    mercury.y_velocity = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 14, WHITE, 4.8685 * 10**24)
    venus.y_velocity = -35.2 * 1000

    planets = [sun, earth, mars, mercury, venus]
    return planets


def main():
    global offset_x
    global offset_y
    global zoom_level

    running = True

    # synchronize simulator, regulate framerate
    clock = pygame.time.Clock()

    planets = config_planets()

    while running:
        clock.tick(60)
        WIND.fill((0, 0, 0))

        # draw zoom buttons
        pygame.draw.rect(WIND, LIGHT_GREY, ZOOM_IN_BUTTON)
        pygame.draw.rect(WIND, LIGHT_GREY, ZOOM_OUT_BUTTON)
        WIND.blit(ZOOM_IN_TEXT, (28, 20))
        WIND.blit(ZOOM_OUT_TEXT, (90, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # keyboard events
            elif event.type == pygame.KEYDOWN:
                # adjust position
                if event.key == pygame.K_LEFT:
                    offset_x -= 10 / zoom_level
                elif event.key == pygame.K_RIGHT:
                    offset_x += 10 / zoom_level
                elif event.key == pygame.K_UP:
                    offset_y -= 10 / zoom_level
                elif event.key == pygame.K_DOWN:
                    offset_y += 10 / zoom_level
                # adjust zoom level
                elif event.key == pygame.K_PLUS:
                    zoom_level *= 1.1
                elif event.key == pygame.K_MINUS:
                    zoom_level /= 1.1

            # mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_position = pygame.mouse.get_pos()
                    if ZOOM_IN_BUTTON.collidepoint(mouse_position):
                        # offset_x = (offset_x + WIDTH / 2 - mouse_position[0]) / 1.1
                        # offset_y = (offset_y + HEIGHT / 2 - mouse_position[1]) / 1.1
                        zoom_level *= 1.1
                    elif ZOOM_OUT_BUTTON.collidepoint(mouse_position):
                        # offset_x = (offset_x + WIDTH / 2 - mouse_position[0]) / 1.1
                        # offset_y = (offset_y + HEIGHT / 2 - mouse_position[1]) / 1.1
                        zoom_level /= 1.1

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIND)

        pygame.display.update()
    
    pygame.quit()

main()
