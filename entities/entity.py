import random
import math
import numpy as np
import pygame
from utils.constants import *

class Entity:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.size = ENTITY_SIZE
        self.energy = MAX_ENERGY
        self.age = 0
        self.direction = random.uniform(0, 2 * math.pi)
        
        # Genetic traits
        if parent:
            # Inherit traits from parent with slight mutation
            self.speed = max(0.5, min(5.0, parent.speed + random.uniform(-0.2, 0.2)))
            self.sense_radius = max(50, min(200, parent.sense_radius + random.uniform(-10, 10)))
            self.color = self._mutate_color(parent.color)
        else:
            # Random initial traits
            self.speed = random.uniform(1.0, 3.0)
            self.sense_radius = random.uniform(50, 150)
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        
        # State
        self.target = None
        self.state = "exploring"  # exploring, seeking_food, reproducing
        self.reproduction_cooldown = 0

    def _mutate_color(self, parent_color):
        return tuple(
            max(50, min(255, c + random.randint(-20, 20)))
            for c in parent_color
        )

    def update(self, world):
        self.age += 1
        self.energy -= ENERGY_CONSUMPTION_RATE * self.speed
        
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # State machine
        if self.energy > REPRODUCTION_THRESHOLD and self.reproduction_cooldown == 0:
            self.state = "reproducing"
        elif self.energy < MAX_ENERGY * 0.5:
            self.state = "seeking_food"
        else:
            self.state = "exploring"

        # Behavior based on state
        if self.state == "seeking_food":
            self._seek_food(world)
        elif self.state == "reproducing":
            self._seek_mate(world)
        else:
            self._explore()

        # Keep within bounds
        self.x = max(0, min(WINDOW_WIDTH, self.x))
        self.y = max(0, min(WINDOW_HEIGHT, self.y))

    def _seek_food(self, world):
        nearest_food = None
        min_dist = float('inf')
        
        for food in world.food:
            dist = math.hypot(food.x - self.x, food.y - self.y)
            if dist < min_dist and dist < self.sense_radius:
                min_dist = dist
                nearest_food = food
        
        if nearest_food:
            angle = math.atan2(nearest_food.y - self.y, nearest_food.x - self.x)
            self.direction = angle
        else:
            self._explore()

    def _seek_mate(self, world):
        nearest_mate = None
        min_dist = float('inf')
        
        for entity in world.entities:
            if (entity != self and 
                entity.state == "reproducing" and 
                entity.energy > REPRODUCTION_THRESHOLD):
                dist = math.hypot(entity.x - self.x, entity.y - self.y)
                if dist < min_dist and dist < self.sense_radius:
                    min_dist = dist
                    nearest_mate = entity
        
        if nearest_mate:
            angle = math.atan2(nearest_mate.y - self.y, nearest_mate.x - self.x)
            self.direction = angle
        else:
            self._explore()

    def _explore(self):
        # Random walk with slight directional persistence
        self.direction += random.uniform(-0.5, 0.5)
        self.direction = self.direction % (2 * math.pi)

    def move(self):
        # Move in current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

    def draw(self, surface):
        # Draw main body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        
        # Draw direction indicator
        end_x = self.x + math.cos(self.direction) * self.size
        end_y = self.y + math.sin(self.direction) * self.size
        pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)
        
        # Draw energy bar
        energy_width = (self.size * 2) * (self.energy / MAX_ENERGY)
        pygame.draw.rect(surface, GREEN, 
                        (self.x - self.size, self.y - self.size - 5, 
                         energy_width, 3))

    def can_reproduce(self):
        return (self.energy > REPRODUCTION_THRESHOLD and 
                self.reproduction_cooldown == 0)

    def reproduce(self):
        self.energy *= 0.5
        self.reproduction_cooldown = 100
        return Entity(self.x, self.y, parent=self) 