import random
import math
import numpy as np
from utils.constants import *
from entities.entity import Entity
from environment.environment import Environment
import pygame
import traceback

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = FOOD_SIZE
        self.quality = random.uniform(*FOOD_QUALITY_RANGE)  # Random quality
        self.energy = FOOD_ENERGY_VALUE * self.quality  # Base energy modified by quality
        self.max_energy = self.energy  # Store initial energy
        self.color = self._get_color()  # Color based on quality
        self.creation_time = pygame.time.get_ticks()
        self.lifetime = FOOD_LIFETIME * 4  # Quadruple the lifetime
        
    def _get_color(self):
        # Color varies from dark green (low quality) to bright green (high quality)
        quality_ratio = (self.quality - FOOD_QUALITY_RANGE[0]) / (FOOD_QUALITY_RANGE[1] - FOOD_QUALITY_RANGE[0])
        r = int(50 + quality_ratio * 50)  # Red component
        g = int(150 + quality_ratio * 105)  # Green component
        b = int(50 + quality_ratio * 50)  # Blue component
        return (r, g, b)
        
    def update(self):
        # Food decays over time
        current_time = pygame.time.get_ticks()
        age = (current_time - self.creation_time) / 1000  # Convert to seconds
        
        # Exponential decay of energy
        decay_factor = math.exp(-FOOD_DECAY_RATE * 0.25 * age)  # Reduce decay rate
        self.energy = self.max_energy * decay_factor
        
        if age > self.lifetime or self.energy < 1:
            return False  # Food should be removed
        return True  # Food is still good
        
    def draw(self, surface):
        try:
            # Draw food with size and color based on remaining energy
            energy_ratio = self.energy / self.max_energy
            current_size = int(self.size * energy_ratio)
            
            # Draw outer circle (quality indicator)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), current_size + 2)
            
            # Draw inner circle (energy indicator)
            inner_color = (int(self.color[0] * energy_ratio), 
                         int(self.color[1] * energy_ratio), 
                         int(self.color[2] * energy_ratio))
            pygame.draw.circle(surface, inner_color, (int(self.x), int(self.y)), current_size)
        except Exception as e:
            print(f"Error drawing food: {e}")

class Garden:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GARDEN_SIZE
        self.food_count = 0
        self.last_spawn_time = pygame.time.get_ticks()
        
    def update(self):
        # Grow food in garden
        if self.food_count < GARDEN_MAX_FOOD and random.random() < GARDEN_GROWTH_RATE * 0.5:  # Reduce growth rate
            self.food_count += 1
            
        # Spawn food less frequently
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_spawn_time > 2000 and  # Only spawn every 2 seconds
            self.food_count > 0 and 
            random.random() < FOOD_SPAWN_RATE * 0.25):  # Further reduce spawn rate
            # Spawn food near garden
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, FOOD_SPAWN_RADIUS)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            
            # Ensure food spawns within bounds
            x = max(0, min(x, WINDOW_WIDTH))
            y = max(0, min(y, WINDOW_HEIGHT))
            
            if len(self.food) < MAX_FOOD:
                self.food.append(Food(x, y))
                self.food_count -= 1
                self.last_spawn_time = current_time
        
    def draw(self, surface):
        try:
            # Draw garden area
            pygame.draw.circle(surface, LIGHT_BLUE, (int(self.x), int(self.y)), self.size, 2)
            # Draw food indicators
            for i in range(self.food_count):
                angle = i * (2 * math.pi / GARDEN_MAX_FOOD)
                x = self.x + math.cos(angle) * (self.size * 0.5)
                y = self.y + math.sin(angle) * (self.size * 0.5)
                pygame.draw.circle(surface, GREEN, (int(x), int(y)), 4)
        except Exception as e:
            print(f"Error drawing garden: {e}")

class World:
    def __init__(self):
        self.entities = []
        self.food = []
        self.gardens = []
        self.environment = Environment()
        self.selected_entity = None
        self.update_counter = 0
        self.spatial_hash = {}  # For spatial partitioning
        
    def _update_spatial_hash(self):
        """Update spatial partitioning for faster neighbor queries"""
        self.spatial_hash = {}
        cell_size = 50  # Size of spatial hash cells
        
        # Hash entities
        for entity in self.entities:
            cell_x = int(entity.x // cell_size)
            cell_y = int(entity.y // cell_size)
            cell_key = (cell_x, cell_y)
            if cell_key not in self.spatial_hash:
                self.spatial_hash[cell_key] = {'entities': [], 'food': [], 'gardens': []}
            self.spatial_hash[cell_key]['entities'].append(entity)
            
        # Hash food
        for food in self.food:
            cell_x = int(food.x // cell_size)
            cell_y = int(food.y // cell_size)
            cell_key = (cell_x, cell_y)
            if cell_key not in self.spatial_hash:
                self.spatial_hash[cell_key] = {'entities': [], 'food': [], 'gardens': []}
            self.spatial_hash[cell_key]['food'].append(food)
            
        # Hash gardens
        for garden in self.gardens:
            cell_x = int(garden.x // cell_size)
            cell_y = int(garden.y // cell_size)
            cell_key = (cell_x, cell_y)
            if cell_key not in self.spatial_hash:
                self.spatial_hash[cell_key] = {'entities': [], 'food': [], 'gardens': []}
            self.spatial_hash[cell_key]['gardens'].append(garden)
            
    def _get_nearby_objects(self, x, y, radius):
        """Get objects within radius using spatial partitioning"""
        cell_size = 50
        cell_x = int(x // cell_size)
        cell_y = int(y // cell_size)
        radius_cells = int(radius // cell_size) + 1
        
        nearby_objects = {'entities': [], 'food': [], 'gardens': []}
        
        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                cell_key = (cell_x + dx, cell_y + dy)
                if cell_key in self.spatial_hash:
                    cell = self.spatial_hash[cell_key]
                    for obj_type in nearby_objects:
                        for obj in cell[obj_type]:
                            if math.hypot(obj.x - x, obj.y - y) <= radius:
                                nearby_objects[obj_type].append(obj)
                                
        return nearby_objects
        
    def update(self):
        try:
            self.update_counter += 1
            
            # Update spatial partitioning every 10 frames
            if self.update_counter % 10 == 0:
                self._update_spatial_hash()
            
            # Update environment
            self.environment.update()
            
            # Update gardens and spawn food
            for garden in self.gardens:
                garden.update()
            
            # Update food with decay
            self.food = [food for food in self.food if food.update()]
            
            # Update entities in batches
            batch_size = 5  # Process 5 entities at a time
            for i in range(0, len(self.entities), batch_size):
                batch = self.entities[i:i+batch_size]
                for entity in batch:
                    try:
                        # Get nearby objects using spatial partitioning
                        nearby = self._get_nearby_objects(entity.x, entity.y, entity.sense_radius)
                        
                        # Update entity state
                        entity.update(self)
                        
                        # Check for garden effects
                        for garden in nearby['gardens']:
                            if math.hypot(entity.x - garden.x, entity.y - garden.y) < garden.size:
                                entity.energy = min(MAX_ENERGY, entity.energy + GARDEN_ENERGY_BOOST)
                        
                        # Check for food consumption
                        for food in nearby['food']:
                            if math.hypot(entity.x - food.x, entity.y - food.y) < entity.size + food.size:
                                entity.energy = min(MAX_ENERGY, entity.energy + food.energy)
                                if food in self.food:  # Check if food still exists
                                    self.food.remove(food)
                        
                        # Check for reproduction with nearby entities
                        if entity.can_reproduce() and len(self.entities) < MAX_ENTITIES:
                            for other in nearby['entities']:
                                if (other != entity and 
                                    other.can_reproduce() and 
                                    math.hypot(entity.x - other.x, entity.y - other.y) < entity.size + other.size):
                                    new_entity = entity.reproduce()
                                    self.entities.append(new_entity)
                                    break
                    except Exception as e:
                        print(f"Error updating entity: {e}")
                        continue
            
            # Remove dead entities and update selected entity
            dead_entities = [entity for entity in self.entities if not entity.is_alive()]
            for entity in dead_entities:
                if entity == self.selected_entity:
                    self.selected_entity = None
            self.entities = [entity for entity in self.entities if entity.is_alive()]
            
            # Limit population if too large
            if len(self.entities) > MAX_ENTITIES * 1.5:
                self.entities = self.entities[:MAX_ENTITIES]
            
        except Exception as e:
            print(f"Error in world update: {e}")
            traceback.print_exc()
    
    def draw(self, surface):
        try:
            # Draw environment
            self.environment.draw(surface)
            
            # Draw gardens
            for garden in self.gardens:
                garden.draw(surface)
            
            # Draw food
            for food in self.food:
                food.draw(surface)
            
            # Draw entities
            for entity in self.entities:
                try:
                    entity.draw(surface)
                    
                    # Highlight selected entity
                    if entity == self.selected_entity:
                        pygame.draw.circle(surface, YELLOW, 
                                         (int(entity.x), int(entity.y)), 
                                         entity.size + 4, 2)
                        # Draw care radius
                        pygame.draw.circle(surface, YELLOW, 
                                         (int(entity.x), int(entity.y)), 
                                         CARE_RADIUS, 1)
                except Exception as e:
                    print(f"Error drawing entity: {e}")
                    
        except Exception as e:
            print(f"Error in world draw: {e}")
    
    def add_entity(self, x, y):
        try:
            if len(self.entities) < MAX_ENTITIES:
                self.entities.append(Entity(x, y))
        except Exception as e:
            print(f"Error adding entity: {e}")
            
    def add_garden(self, x, y):
        if len(self.gardens) < MAX_GARDENS:
            # Check if position is valid (not too close to other gardens)
            valid_position = True
            for garden in self.gardens:
                distance = math.sqrt((x - garden.x)**2 + (y - garden.y)**2)
                if distance < GARDEN_SIZE * 2:
                    valid_position = False
                    break
            
            if valid_position:
                self.gardens.append(Garden(x, y))
                return True
        return False
        
    def select_entity_at(self, x, y):
        try:
            self.selected_entity = None
            for entity in self.entities:
                if math.hypot(x - entity.x, y - entity.y) < entity.size:
                    self.selected_entity = entity
                    break
        except Exception as e:
            print(f"Error selecting entity: {e}")
                
    def heal_selected_entity(self):
        try:
            if self.selected_entity:
                self.selected_entity.energy = min(MAX_ENERGY, 
                                                self.selected_entity.energy + HEALING_AMOUNT)
                self.selected_entity.health = min(100, self.selected_entity.health + 20)
        except Exception as e:
            print(f"Error healing entity: {e}")
            
    def feed_nearby_entities(self, x, y):
        try:
            for entity in self.entities:
                if math.hypot(x - entity.x, y - entity.y) < CARE_RADIUS:
                    entity.energy = min(MAX_ENERGY, entity.energy + FEEDING_AMOUNT)
        except Exception as e:
            print(f"Error feeding entities: {e}") 