import pygame
import random
import math
import numpy as np
from utils.constants import *

class Environment:
    def __init__(self):
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.cell_size = 32
        self.grid_width = self.width // self.cell_size
        self.grid_height = self.height // self.cell_size
        self.terrain = self.generate_terrain()
        self.elevation = self.generate_elevation()
        self.weather = WEATHER_CLEAR
        self.temperature = random.uniform(*TEMPERATURE_RANGE)
        self.weather_timer = 0
        self.weather_duration = random.randint(300, 600)
        self.season = 0  # 0: spring, 1: summer, 2: fall, 3: winter
        self.season_timer = 0
        self.season_duration = 2000  # Duration of each season in ticks
        self.time_of_day = 0  # 0-23 hours
        self.day_timer = 0
        self.day_duration = 100  # Duration of each hour in ticks
        
    def generate_terrain(self):
        # Use Perlin noise for more natural terrain
        noise = np.zeros((self.grid_height, self.grid_width))
        scale = 0.1
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                noise[y][x] = math.sin(x * scale) * math.cos(y * scale)
        
        # Initialize terrain
        terrain = [[TERRAIN_GRASS for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Create water bodies and other terrain features
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                value = noise[y][x]
                if value < -0.3:
                    terrain[y][x] = TERRAIN_WATER
                elif value > 0.3:
                    terrain[y][x] = TERRAIN_ROCK
                elif value > 0.1:
                    terrain[y][x] = TERRAIN_SAND
                    
        # Add special features
        for _ in range(5):  # Add some hot springs
            x = random.randint(0, self.grid_width-1)
            y = random.randint(0, self.grid_height-1)
            terrain[y][x] = TERRAIN_SPRING
            
        for _ in range(3):  # Add some nests
            x = random.randint(0, self.grid_width-1)
            y = random.randint(0, self.grid_height-1)
            terrain[y][x] = TERRAIN_NEST
            
        return terrain
        
    def generate_elevation(self):
        # Generate elevation map using Perlin noise
        elevation = np.zeros((self.grid_height, self.grid_width))
        scale = 0.05
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                elevation[y][x] = math.sin(x * scale) * math.cos(y * scale)
        return elevation
        
    def update_weather(self):
        self.weather_timer += 1
        if self.weather_timer >= self.weather_duration:
            self.weather_timer = 0
            self.weather_duration = random.randint(300, 600)
            
            # Weather changes based on season
            if self.season == 0:  # Spring
                self.weather = random.choice([WEATHER_CLEAR, WEATHER_RAIN])
            elif self.season == 1:  # Summer
                self.weather = random.choice([WEATHER_CLEAR, WEATHER_STORM])
            elif self.season == 2:  # Fall
                self.weather = random.choice([WEATHER_CLEAR, WEATHER_RAIN])
            else:  # Winter
                self.weather = random.choice([WEATHER_CLEAR, WEATHER_SNOW])
                
    def update_temperature(self):
        # Base temperature varies by season
        season_base = {
            0: 15,  # Spring
            1: 25,  # Summer
            2: 15,  # Fall
            3: 0    # Winter
        }
        
        # Daily temperature variation
        daily_variation = math.sin(self.time_of_day * math.pi / 12) * 5
        
        # Weather effects
        weather_effect = {
            WEATHER_CLEAR: 0,
            WEATHER_RAIN: -5,
            WEATHER_SNOW: -10,
            WEATHER_STORM: -3
        }
        
        # Calculate new temperature
        base_temp = season_base[self.season]
        self.temperature = base_temp + daily_variation + weather_effect[self.weather]
        
    def update_season(self):
        self.season_timer += 1
        if self.season_timer >= self.season_duration:
            self.season_timer = 0
            self.season = (self.season + 1) % 4
            
    def update_time(self):
        self.day_timer += 1
        if self.day_timer >= self.day_duration:
            self.day_timer = 0
            self.time_of_day = (self.time_of_day + 1) % 24
            
    def get_terrain_effect(self, x, y):
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return {'speed_multiplier': 1.0, 'energy_drain': 1.0}
            
        terrain_type = self.terrain[grid_y][grid_x]
        elevation = self.elevation[grid_y][grid_x]
        
        effects = {
            TERRAIN_WATER: {'speed_multiplier': 0.5, 'energy_drain': 1.5},
            TERRAIN_SAND: {'speed_multiplier': 0.8, 'energy_drain': 1.2},
            TERRAIN_GRASS: {'speed_multiplier': 1.0, 'energy_drain': 1.0},
            TERRAIN_ROCK: {'speed_multiplier': 0.6, 'energy_drain': 1.3},
            TERRAIN_GARDEN: {'speed_multiplier': 1.2, 'energy_drain': 0.8},
            TERRAIN_SPRING: {'speed_multiplier': 1.0, 'energy_drain': 0.7},
            TERRAIN_NEST: {'speed_multiplier': 0.9, 'energy_drain': 0.6}
        }
        
        # Apply elevation effect
        elevation_effect = 1.0 + elevation * 0.2
        effect = effects[terrain_type]
        return {
            'speed_multiplier': effect['speed_multiplier'] / elevation_effect,
            'energy_drain': effect['energy_drain'] * elevation_effect
        }
        
    def get_weather_effect(self):
        effects = {
            WEATHER_CLEAR: {'speed_multiplier': 1.0, 'energy_drain': 1.0},
            WEATHER_RAIN: {'speed_multiplier': 0.9, 'energy_drain': 1.2},
            WEATHER_SNOW: {'speed_multiplier': 0.7, 'energy_drain': 1.5},
            WEATHER_STORM: {'speed_multiplier': 0.6, 'energy_drain': 1.8}
        }
        return effects[self.weather]
        
    def update(self):
        self.update_weather()
        self.update_temperature()
        self.update_season()
        self.update_time()
        
    def draw(self, screen):
        # Apply time of day lighting
        base_ambient = self._get_ambient_light()
        
        # Create time-of-day overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill(self._get_sky_color())
        overlay.set_alpha(base_ambient)
        screen.blit(overlay, (0, 0))
        
        # Draw terrain with elevation shading
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                 self.cell_size, self.cell_size)
                
                # Base terrain color
                colors = {
                    TERRAIN_WATER: (0, 100, 255),  # Deeper blue for water
                    TERRAIN_SAND: (194, 178, 128),
                    TERRAIN_GRASS: (34, 139, 34),  # Forest green
                    TERRAIN_ROCK: (128, 128, 128),
                    TERRAIN_GARDEN: (0, 255, 128),  # Brighter green with blue tint
                    TERRAIN_SPRING: (255, 165, 0),
                    TERRAIN_NEST: (139, 69, 19)
                }
                
                color = colors[self.terrain[y][x]]
                
                # Apply elevation shading
                elevation = self.elevation[y][x]
                shade = int(255 * (0.5 + elevation * 0.5))
                color = tuple(min(255, max(0, c + shade - 128)) for c in color)
                
                # Apply seasonal color modifications
                season_mods = self._get_season_colors()
                color = tuple(min(255, max(0, c + season_mods[i])) for i, c in enumerate(color))
                
                # Draw terrain with ambient lighting
                lit_color = tuple(min(255, max(0, int(c * (0.4 + base_ambient * 0.6)))) for c in color)
                pygame.draw.rect(screen, lit_color, rect)
                
                # Draw grid lines with variable opacity
                grid_alpha = int(40 + base_ambient * 60)
                grid_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(grid_surface, (0, 0, 0, grid_alpha), grid_surface.get_rect(), 1)
                screen.blit(grid_surface, rect)
                
                # Add terrain details
                if self.terrain[y][x] == TERRAIN_WATER:
                    # Ripple effect
                    if random.random() < 0.05:
                        ripple_pos = (x * self.cell_size + random.randint(4, self.cell_size-4),
                                    y * self.cell_size + random.randint(4, self.cell_size-4))
                        pygame.draw.circle(screen, (200, 200, 255, 100), ripple_pos, 2, 1)
                elif self.terrain[y][x] == TERRAIN_GARDEN:
                    # Draw flowers
                    for _ in range(2):
                        flower_pos = (x * self.cell_size + random.randint(4, self.cell_size-4),
                                    y * self.cell_size + random.randint(4, self.cell_size-4))
                        pygame.draw.circle(screen, (255, 255, 0), flower_pos, 2)
                elif self.terrain[y][x] == TERRAIN_SPRING:
                    # Steam effect
                    if random.random() < 0.1:
                        steam_pos = (x * self.cell_size + random.randint(4, self.cell_size-4),
                                   y * self.cell_size + random.randint(4, self.cell_size-4))
                        pygame.draw.circle(screen, (255, 255, 255, 100), steam_pos, 2)
        
        # Draw weather effects
        self._draw_weather_effects(screen)
        
    def _get_ambient_light(self):
        # Calculate ambient light based on time of day
        hour = self.time_of_day
        if 6 <= hour < 20:  # Daytime
            # Peak brightness at noon (hour 12)
            return 0.7 + 0.3 * (1.0 - abs(hour - 12) / 6.0)
        else:  # Night time
            # Darkest at midnight (hour 0)
            night_hour = hour if hour < 6 else hour - 20
            return 0.2 + 0.1 * (1.0 - abs(night_hour - 3) / 3.0)
            
    def _get_sky_color(self):
        hour = self.time_of_day
        if 5 <= hour < 7:  # Dawn
            return (255, 200, 150)  # Orange-pink sunrise
        elif 7 <= hour < 17:  # Day
            return (150, 200, 255)  # Light blue day
        elif 17 <= hour < 19:  # Dusk
            return (255, 150, 100)  # Orange-red sunset
        else:  # Night
            return (20, 20, 50)  # Dark blue night
            
    def _get_season_colors(self):
        if self.season == 0:  # Spring
            return (0, 20, 0)  # Slightly more green
        elif self.season == 1:  # Summer
            return (10, 30, -10)  # More vibrant, less blue
        elif self.season == 2:  # Fall
            return (30, -20, -20)  # More red, less green and blue
        else:  # Winter
            return (-20, -20, 20)  # Less red and green, more blue
            
    def _draw_weather_effects(self, screen):
        if self.weather == WEATHER_RAIN:
            rain_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for _ in range(100):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                alpha = random.randint(100, 200)
                pygame.draw.line(rain_surface, (200, 200, 255, alpha), 
                               (x, y), (x - 2, y + 10), 1)
            screen.blit(rain_surface, (0, 0))
            
        elif self.weather == WEATHER_SNOW:
            snow_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for _ in range(50):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                size = random.randint(2, 4)
                alpha = random.randint(150, 255)
                pygame.draw.circle(snow_surface, (255, 255, 255, alpha), 
                                 (x, y), size)
            screen.blit(snow_surface, (0, 0))
            
        elif self.weather == WEATHER_STORM:
            # Dark storm overlay
            storm_overlay = pygame.Surface((self.width, self.height))
            storm_overlay.fill((20, 20, 40))
            storm_overlay.set_alpha(100)
            screen.blit(storm_overlay, (0, 0))
            
            # Lightning effects
            if random.random() < 0.05:
                lightning_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                start_x = random.randint(0, self.width)
                points = [(start_x, 0)]
                for i in range(5):
                    points.append((
                        points[-1][0] + random.randint(-50, 50),
                        (i + 1) * 100
                    ))
                pygame.draw.lines(lightning_surface, (255, 255, 200, 200), 
                                False, points, 3)
                screen.blit(lightning_surface, (0, 0)) 