import random
import math
import numpy as np
from utils.constants import *
from entities.entity import Entity
import pygame

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 5
        self.energy = FOOD_ENERGY_VALUE

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.size)

class World:
    def __init__(self):
        self.entities = []
        self.food = []
        
    def update(self):
        # Update entities
        for entity in self.entities[:]:
            entity.update(self)
            entity.move()
            
            # Check for food consumption
            for food in self.food[:]:
                if math.hypot(entity.x - food.x, entity.y - food.y) < entity.size + food.size:
                    entity.energy = min(MAX_ENERGY, entity.energy + food.energy)
                    self.food.remove(food)
            
            # Check for reproduction
            if entity.can_reproduce():
                for other in self.entities:
                    if (other != entity and 
                        other.can_reproduce() and 
                        math.hypot(entity.x - other.x, entity.y - other.y) < entity.size + other.size):
                        new_entity = entity.reproduce()
                        self.entities.append(new_entity)
                        break
            
            # Remove dead entities
            if entity.energy <= MIN_ENERGY:
                self.entities.remove(entity)
        
        # Spawn new food
        if len(self.food) < MAX_FOOD and random.random() < FOOD_SPAWN_RATE:
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            self.food.append(Food(x, y))
    
    def draw(self, surface):
        # Draw a simple grid instead of terrain for better performance
        for x in range(0, WINDOW_WIDTH, 50):
            pygame.draw.line(surface, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, 50):
            pygame.draw.line(surface, GRAY, (0, y), (WINDOW_WIDTH, y), 1)
        
        # Draw food
        for food in self.food:
            food.draw(surface)
        
        # Draw entities
        for entity in self.entities:
            entity.draw(surface)
    
    def add_entity(self, x, y):
        if len(self.entities) < MAX_ENTITIES:
            self.entities.append(Entity(x, y)) 