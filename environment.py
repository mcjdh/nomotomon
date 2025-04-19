import pygame
import random
import numpy as np
from utils.constants import *
from entities.food import Food
from entities.garden import Garden

class Environment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.food = []
        self.gardens = []
        self.terrain = self.generate_terrain()
        self.temperature = random.uniform(*TEMPERATURE_RANGE)
        self.weather = random.choice(WEATHER_TYPES)
        self.weather_timer = 0
        self.weather_duration = random.randint(100, 500)
        
    def generate_terrain(self):
        # Generate a noise-based terrain map
        terrain = np.zeros((self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                noise = random.random()
                if noise < 0.2:
                    terrain[x][y] = 1  # Water
                elif noise < 0.4:
                    terrain[x][y] = 2  # Sand
                elif noise < 0.6:
                    terrain[x][y] = 3  # Rock
                else:
                    terrain[x][y] = 0  # Grass
        return terrain
        
    def get_terrain_type(self, x, y):
        terrain_id = int(self.terrain[int(x)][int(y)])
        return list(TERRAIN_TYPES.keys())[terrain_id]
        
    def get_terrain_effect(self, x, y):
        terrain_type = self.get_terrain_type(x, y)
        return TERRAIN_TYPES[terrain_type]['speed_multiplier']
        
    def update_weather(self):
        self.weather_timer += 1
        if self.weather_timer >= self.weather_duration:
            self.weather = random.choice(WEATHER_TYPES)
            self.weather_timer = 0
            self.weather_duration = random.randint(100, 500)
            
    def get_weather_effect(self):
        return WEATHER_EFFECTS[self.weather]
        
    def update_temperature(self):
        # Temperature changes based on weather and time
        if self.weather == 'snow':
            self.temperature = max(self.temperature - 0.1, TEMPERATURE_RANGE[0])
        elif self.weather == 'clear':
            self.temperature = min(self.temperature + 0.1, TEMPERATURE_RANGE[1])
            
    def update(self):
        self.update_weather()
        self.update_temperature()
        
        # Update food
        if random.random() < FOOD_SPAWN_RATE and len(self.food) < MAX_FOOD:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.food.append(Food(x, y))
            
        # Update gardens
        for garden in self.gardens:
            garden.update()
            
    def draw(self, screen):
        # Draw terrain
        for x in range(self.width):
            for y in range(self.height):
                terrain_id = int(self.terrain[x][y])
                color = list(TERRAIN_TYPES.values())[terrain_id]['color']
                pygame.draw.rect(screen, color, (x, y, 1, 1))
                
        # Draw weather effects
        if self.weather == 'rain':
            for _ in range(50):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                pygame.draw.line(screen, (200, 200, 255), (x, y), (x, y+5), 1)
        elif self.weather == 'snow':
            for _ in range(30):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)
                
        # Draw food
        for food in self.food:
            food.draw(screen)
            
        # Draw gardens
        for garden in self.gardens:
            garden.draw(screen)
            
        # Draw weather and temperature info
        font = pygame.font.SysFont(None, 24)
        weather_text = font.render(f'Weather: {self.weather}, Temp: {self.temperature:.1f}°C', True, WHITE)
        screen.blit(weather_text, (10, 10)) 