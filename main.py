import pygame
import sys
import random
import matplotlib.pyplot as plt
from pygame.locals import *
from entities.entity import Entity
from world.world import World
from utils.constants import *

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Nomotomon - Life Simulator')
clock = pygame.time.Clock()

# Create world
world = World()

# Add initial entities
for _ in range(INITIAL_ENTITIES):
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    world.add_entity(x, y)

# Statistics
population_history = []
energy_history = []
font = pygame.font.Font(None, 24)

def draw_stats(surface):
    # Draw current stats
    stats = [
        f"Population: {len(world.entities)}",
        f"Food: {len(world.food)}",
        f"FPS: {int(clock.get_fps())}"
    ]
    
    for i, stat in enumerate(stats):
        text = font.render(stat, True, WHITE)
        surface.blit(text, (10, 10 + i * 25))

# Main game loop
running = True
paused = False
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_SPACE:
                paused = not paused
            elif event.key == K_r:  # Reset simulation
                world = World()
                for _ in range(INITIAL_ENTITIES):
                    x = random.randint(0, WINDOW_WIDTH)
                    y = random.randint(0, WINDOW_HEIGHT)
                    world.add_entity(x, y)
        elif event.type == MOUSEBUTTONDOWN:
            # Add new entity on mouse click
            x, y = pygame.mouse.get_pos()
            world.add_entity(x, y)

    if not paused:
        # Update world
        world.update()
        
        # Record statistics
        population_history.append(len(world.entities))
        if len(population_history) > 1000:  # Keep last 1000 frames
            population_history.pop(0)
        
        if world.entities:
            avg_energy = sum(e.energy for e in world.entities) / len(world.entities)
            energy_history.append(avg_energy)
            if len(energy_history) > 1000:
                energy_history.pop(0)

    # Draw everything
    screen.fill(BLACK)
    world.draw(screen)
    draw_stats(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
sys.exit() 