import pygame 
import math
from datetime import datetime
from skyfield.api import load
import json
import random

pygame.init()

from star import Star
from planet import Planet

WIDTH, HEIGHT = 1200, 800
WIND = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulator")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 80)
LIGHT_GREY = (211, 211, 211)

FONT = pygame.font.SysFont("comicsans", 16)

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

def config_planets():
    # load data from .json (change to attributes of Planet class later)
    with open('planet_data.json', 'r') as json_file:
        planets_data = json.load(json_file)

    ts = load.timescale()
    t = ts.now()

    skyfield = load("de421.bsp")

    image = pygame.image.load('images/sun.png')
    resized_img = pygame.transform.scale(image, (40, 40))

    sun = Planet("sun", resized_img, 0, 0, 30, YELLOW, 1.98892 * 10 **30) # in kg
    sun.sun = True
    planets = [sun]

    for key, data in planets_data.items():
        skyfield_key = key + " " + 'barycenter'
        planet_name = skyfield[skyfield_key]
        mass = float(data["mass"])
        colour = data["colour"]
        orbital_velocity = float(data["orbital_velocity"])

        # obtain position of planets relative to the Sun
        astrometric = planet_name.at(t)
        apparent_positions = astrometric.observe(skyfield['sun'])
        x_pos, y_pos, _ = apparent_positions.position.au

        # load planet image
        img_filename = f"images/{key}.png"
        image = pygame.image.load(img_filename)
        resized_img = pygame.transform.scale(image, (40, 40))

        planet = Planet(key, resized_img, x_pos * Planet.AU, y_pos * Planet.AU, 12, colour, mass * 10 **24)
        planet.y_velocity = orbital_velocity * 1000
        planets.append(planet)

    return planets


def draw_legend(planets):
    legend_x = WIDTH - 300
    legend_y = 10
    legend_spacing = 30
    legend_width = 275
    legend_height = len(planets) * legend_spacing

    # surface for the legend
    legend_surface = pygame.Surface((legend_width, legend_height))
    legend_surface.fill((0, 0, 0))
    legend_surface.set_alpha(200)  # transparency

    for planet in planets:
        if not planet.sun:
            distance_text = FONT.render(f"{planet.distance_to_sun / 1000:.1f} km", 1, WHITE)
            name_text = FONT.render(planet.name, 1, planet.colour)
            legend_surface.blit(name_text, (10, legend_y))
            legend_surface.blit(distance_text, (120, legend_y))
            legend_y += legend_spacing

    # border around the legend
    pygame.draw.rect(legend_surface, WHITE, legend_surface.get_rect(), 2)

    # legend surface onto main window
    WIND.blit(legend_surface, (legend_x, 10))


def main():
    global offset_x
    global offset_y
    global zoom_level

    running = True
    paused = True       # pause simulation initially
    dragging = False    # drag and pan

    # synchronize simulator, regulate framerate
    clock = pygame.time.Clock()

    planets = config_planets()
    stars = [Star(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]


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
                # pause/resume simulation
                if event.key == pygame.K_SPACE:
                    paused = not paused
                # adjust position
                elif event.key == pygame.K_LEFT:
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
                    dragging = True
                    mouse_position = pygame.mouse.get_pos()
                    if ZOOM_IN_BUTTON.collidepoint(mouse_position):
                        zoom_level *= 1.1
                    elif ZOOM_OUT_BUTTON.collidepoint(mouse_position):
                        zoom_level /= 1.1
                elif event.button == 4:     # mouse wheel up (zoom in)
                    zoom_level *= 1.1
                elif event.button == 5:     # mouse wheel down (zoom out)
                    zoom_level /= 1.1
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

        # handle mouse/mousepad drag and pan
        if dragging:
            drag_mouse_position = pygame.mouse.get_pos()
            if mouse_position:
                dx = drag_mouse_position[0] - mouse_position[0]
                dy = drag_mouse_position[1] - mouse_position[1]
                offset_x -= dx
                offset_y -= dy
            mouse_position = drag_mouse_position

        for star in stars:
            star.update()
            star.draw(WIND)

        for planet in planets:
            if not paused:
                planet.update_position(planets)
            planet.draw(WIND, WIDTH, HEIGHT, offset_x, offset_y, zoom_level)

        draw_legend(planets)

        pygame.display.update()
    
    pygame.quit()

main()
