import random
import math
import numpy as np
import pygame
from utils.constants import *
from entities.brain import NeuralNetwork
from utils.genetics import Genetics
import traceback

class Entity:
    def __init__(self, x, y, genetics=None):
        self.x = x
        self.y = y
        self.genetics = genetics if genetics else Genetics()
        self.energy = INITIAL_ENERGY
        self.age = 0
        self.body_parts = self.generate_body_parts()
        self.direction = random.uniform(0, 2 * math.pi)
        self.speed = self.calculate_speed()
        self.health = 100
        self.temperature = TEMPERATURE_RANGE[1]  # Start at comfortable temperature
        self.base_speed = self.speed  # Store base speed for environmental adjustments
        
        # Calculate size based on body parts
        self.size = self.body_parts['body']['size']  # Base size on body size
        
        # Initialize brain
        self.brain = NeuralNetwork(None)
        self.species_name = self.brain.species_name
        
        # Genetic traits
        self.sense_radius = random.uniform(50, 150)
        self.color = self._mutate_color((255, 255, 255))
        
        # State
        self.target = None
        self.state = "exploring"
        self.reproduction_cooldown = 0
        self.last_action = None
        self.success_count = 0
        self.environmental_effects = {
            'weather': {'speed_multiplier': 1.0, 'energy_drain': 1.0},
            'terrain': {'speed_multiplier': 1.0, 'energy_drain': 1.0}
        }
        
        # Add tracking variables for reward calculation
        self.last_energy = self.energy
        self.last_health = self.health
        self.last_food_distance = float('inf')
        
        # Social and Learning attributes
        self.memories = []  # Store experiences and interactions
        self.social_bonds = {}  # Track relationships with other entities
        self.learned_behaviors = set()  # Set of behaviors learned from others
        self.teaching_cooldown = 0
        self.learning_rate = random.uniform(0.05, 0.15)  # Individual learning capability
        self.social_disposition = random.uniform(0.3, 0.9)  # Tendency to interact
        self.generation = 0 if not genetics else genetics.generation + 1

    def generate_body_parts(self):
        body_parts = {}
        for part_name, part_data in BODY_PARTS.items():
            size = random.uniform(part_data['size'][0], part_data['size'][1])
            body_parts[part_name] = {
                'size': size,
                'color': part_data['color'],
                'health': 100,
                'temperature_resistance': random.uniform(0.5, 1.5)  # How well this part handles temperature
            }
        return body_parts
        
    def calculate_speed(self):
        base_speed = self.genetics.get_trait('speed')
        # Adjust speed based on body part sizes
        leg_size = self.body_parts['legs']['size']
        body_size = self.body_parts['body']['size']
        size_factor = leg_size / body_size
        return base_speed * size_factor
        
    def update_health(self):
        # Update health based on body part conditions and environmental effects
        total_health = 0
        for part_name, part in self.body_parts.items():
            # Environmental effects on body parts
            if part_name == 'legs':
                # Legs are more affected by terrain
                part['health'] -= (self.environmental_effects['terrain']['energy_drain'] - 1) * 0.1
            elif part_name == 'body':
                # Body is more affected by weather
                part['health'] -= (self.environmental_effects['weather']['energy_drain'] - 1) * 0.1
            elif part_name == 'head':
                # Head is more affected by temperature
                temp_diff = abs(self.temperature - TEMPERATURE_RANGE[1])
                part['health'] -= temp_diff * 0.01
            
            # Ensure health stays within bounds
            part['health'] = max(0, min(100, part['health']))
            total_health += part['health']
            
        self.health = total_health / len(self.body_parts)
        
    def update_temperature(self, environment_temperature):
        # Adjust entity temperature based on environment and body parts
        temp_diff = environment_temperature - self.temperature
        temp_resistance = sum(part['temperature_resistance'] for part in self.body_parts.values()) / len(self.body_parts)
        self.temperature += temp_diff * 0.01 * temp_resistance
        
        # Temperature effects on health
        if self.temperature < TEMPERATURE_RANGE[0] or self.temperature > TEMPERATURE_RANGE[1]:
            for part in self.body_parts.values():
                part['health'] -= 0.1 * (1 - part['temperature_resistance'])
            
    def update(self, world):
        try:
            # Only update every few frames based on speed
            if random.random() > min(0.1, self.speed / 10.0):
                return
                
            # Get current grid position
            grid_x = int(self.x // world.environment.cell_size)
            grid_y = int(self.y // world.environment.cell_size)
            
            # Ensure grid coordinates are within bounds
            grid_x = max(0, min(world.environment.grid_width - 1, grid_x))
            grid_y = max(0, min(world.environment.grid_height - 1, grid_y))
            
            # Get terrain type at current position
            terrain_type = world.environment.terrain[grid_y][grid_x]
            
            # Calculate elevation
            elevation = grid_y / world.environment.grid_height
            
            # Get nearby objects using spatial partitioning
            nearby = world._get_nearby_objects(self.x, self.y, self.sense_radius)
            
            # Find nearest food, mate, and garden from nearby objects
            nearest_food = self._find_nearest_food(nearby['food'])
            nearest_mate = self._find_nearest_mate(nearby['entities'])
            nearest_garden = self._find_nearest_garden(nearby['gardens'])
            
            # Prepare neural network inputs
            inputs = [
                self.energy / MAX_ENERGY,
                self.health / 100.0,
                self.temperature / TEMPERATURE_RANGE[1],
                grid_x / world.environment.grid_width,
                grid_y / world.environment.grid_height,
                terrain_type / 7.0,  # Normalize terrain type
                (nearest_food.x - self.x) / world.environment.width if nearest_food else 0,
                (nearest_food.y - self.y) / world.environment.height if nearest_food else 0,
                (nearest_mate.x - self.x) / world.environment.width if nearest_mate else 0,
                (nearest_mate.y - self.y) / world.environment.height if nearest_mate else 0,
                (nearest_garden.x - self.x) / world.environment.width if nearest_garden else 0,
                (nearest_garden.y - self.y) / world.environment.height if nearest_garden else 0,
                world.environment.weather / 4.0,  # Normalize weather
                elevation
            ]
            
            # Get neural network outputs
            outputs = self.brain.think(inputs)
            
            # Apply movement based on outputs
            self.direction += outputs['direction_change'] * 0.1
            self.speed = self.base_speed * outputs['speed_multiplier']
            self.move()
            
            # Handle social interactions
            if outputs['social_interaction'] > 0.7:
                self.interact_with_nearby_entities(nearby['entities'])
                
            # Handle garden building
            if (outputs['garden_building'] > 0.8 and 
                self.energy > MAX_ENERGY * 0.7 and 
                len(world.gardens) < MAX_GARDENS):
                # Check if we're in a good spot to build a garden
                nearby_gardens = sum(1 for g in nearby['gardens'] 
                                   if math.hypot(g.x - self.x, g.y - self.y) < GARDEN_SIZE * 2)
                if nearby_gardens == 0:  # No gardens too close
                    world.add_garden(self.x, self.y)
                    self.energy *= 0.7  # Cost of building garden
            
            # Update health and energy based on terrain
            self.update_health()
            self.energy -= self.calculate_energy_cost(terrain_type)
            
            # Handle reproduction
            if outputs['reproduction_urge'] > 0.8 and self.can_reproduce():
                self.reproduce()
            
            # Learn from experience
            reward = self._calculate_reward(world)
            self.brain.learn({
                'inputs': inputs,
                'outputs': [outputs['speed_multiplier'] - 1.0, 
                          outputs['direction_change'],
                          outputs['reproduction_urge'],
                          outputs['grid_movement'],
                          outputs['social_interaction'],
                          outputs['garden_building']],
                'reward': reward
            })
            
            # Update age and cooldowns
            self.age += 1
            self.reproduction_cooldown = max(0, self.reproduction_cooldown - 1)
            self.teaching_cooldown = max(0, self.teaching_cooldown - 1)
            
        except Exception as e:
            print(f"Error updating entity: {e}")
            traceback.print_exc()
            
    def calculate_energy_cost(self, terrain_type):
        # Different terrains have different energy costs
        base_cost = 0.1
        if terrain_type == TERRAIN_WATER:
            return base_cost * 2.0
        elif terrain_type == TERRAIN_SAND:
            return base_cost * 1.5
        elif terrain_type == TERRAIN_ROCK:
            return base_cost * 1.8
        elif terrain_type == TERRAIN_GARDEN:
            return base_cost * 0.5
        elif terrain_type == TERRAIN_SPRING:
            return base_cost * 0.7
        elif terrain_type == TERRAIN_NEST:
            return base_cost * 0.6
        else:  # TERRAIN_GRASS
            return base_cost

    def _mutate_color(self, parent_color):
        return tuple(
            max(50, min(255, c + random.randint(-20, 20)))
            for c in parent_color
        )

    def _find_nearest_food(self, food_list):
        nearest = None
        min_dist = float('inf')
        for food in food_list:
            dist = math.hypot(food.x - self.x, food.y - self.y)
            if dist < min_dist and dist < self.sense_radius:
                min_dist = dist
                nearest = food
        return nearest

    def _find_nearest_mate(self, entity_list):
        nearest = None
        min_dist = float('inf')
        for entity in entity_list:
            if (entity != self and 
                entity.can_reproduce() and 
                entity.energy > REPRODUCTION_THRESHOLD and
                entity.health > 50):
                dist = math.hypot(entity.x - self.x, entity.y - self.y)
                if dist < min_dist and dist < self.sense_radius:
                    min_dist = dist
                    nearest = entity
        return nearest

    def _find_nearest_garden(self, garden_list):
        nearest = None
        min_dist = float('inf')
        for garden in garden_list:
            dist = math.hypot(garden.x - self.x, garden.y - self.y)
            if dist < min_dist and dist < self.sense_radius:
                min_dist = dist
                nearest = garden
        return nearest

    def _calculate_reward(self, world):
        reward = 0.0
        
        # Base survival reward
        reward += 0.1  # Small constant reward for staying alive
        
        # Energy reward
        energy_change = self.energy - self.last_energy
        reward += energy_change * 0.5
        
        # Health reward
        health_change = self.health - self.last_health
        reward += health_change * 0.3
        
        # Garden interaction reward
        for garden in world.gardens:
            if math.hypot(self.x - garden.x, self.y - garden.y) < garden.size:
                reward += 0.2  # Reward for being in a garden
        
        # Social interaction reward
        if len(self.social_bonds) > 0:
            reward += 0.1 * len(self.social_bonds)  # Reward for having social bonds
        
        # Learning reward
        if len(self.learned_behaviors) > 0:
            reward += 0.05 * len(self.learned_behaviors)  # Reward for learning
        
        # Garden building reward
        if any(math.hypot(self.x - g.x, self.y - g.y) < 10 for g in world.gardens):
            reward += 0.3  # Reward for being near a garden you built
        
        # Penalize corner-seeking behavior
        center_x = world.environment.width / 2
        center_y = world.environment.height / 2
        distance_from_center = math.hypot(self.x - center_x, self.y - center_y)
        max_distance = math.hypot(center_x, center_y)
        reward -= (distance_from_center / max_distance) * 0.1  # Penalty for being far from center
        
        # Update last values
        self.last_energy = self.energy
        self.last_health = self.health
        
        return reward

    def move(self):
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

    def draw(self, screen):
        # Draw body parts with environmental effects
        for part_name, part_data in self.body_parts.items():
            size = part_data['size']
            color = list(part_data['color'])  # Convert to list for modification
            
            # Adjust color based on health
            health_factor = part_data['health'] / 100
            color = [int(c * health_factor) for c in color]
            
            if part_name == 'body':
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(size))
            elif part_name == 'head':
                head_x = self.x + math.cos(self.direction) * (self.body_parts['body']['size'] + size/2)
                head_y = self.y + math.sin(self.direction) * (self.body_parts['body']['size'] + size/2)
                pygame.draw.circle(screen, color, (int(head_x), int(head_y)), int(size))
            elif part_name == 'legs':
                for i in range(4):  # Draw 4 legs
                    angle = self.direction + (i - 1.5) * 0.5
                    leg_x = self.x + math.cos(angle) * self.body_parts['body']['size']
                    leg_y = self.y + math.sin(angle) * self.body_parts['body']['size']
                    pygame.draw.line(screen, color, (int(self.x), int(self.y)), 
                                   (int(leg_x), int(leg_y)), int(size))
                    
        # Draw health bar
        health_width = 20
        health_height = 3
        health_x = self.x - health_width/2
        health_y = self.y - self.body_parts['body']['size'] - 5
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, health_width * (self.health/100), health_height))
        
        # Draw temperature indicator
        temp_color = (255, 0, 0) if self.temperature > TEMPERATURE_RANGE[1] else (0, 0, 255)
        pygame.draw.circle(screen, temp_color, (int(self.x), int(self.y)), 2)
        
        # Draw environmental effect indicators
        if self.environmental_effects['weather']['speed_multiplier'] < 1.0:
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y) + 10), 2)
        if self.environmental_effects['terrain']['speed_multiplier'] < 1.0:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y) + 15), 2)
        
        # Draw social indicators
        if self.social_bonds:
            # Draw connection lines to bonded entities
            for other, bond in self.social_bonds.items():
                if bond['trust'] > 0.7:  # Only show strong bonds
                    pygame.draw.line(screen, (0, 255, 0, int(bond['trust'] * 128)),
                                   (int(self.x), int(self.y)),
                                   (int(other.x), int(other.y)), 1)
                                   
        # Draw generation indicator
        font = pygame.font.Font(None, 20)
        gen_text = font.render(f"G{self.generation}", True, (255, 255, 255))
        screen.blit(gen_text, (self.x + 15, self.y - 15))

    def can_reproduce(self):
        return (self.energy > REPRODUCTION_THRESHOLD and 
                self.reproduction_cooldown == 0 and
                self.health > 50)

    def reproduce(self):
        self.energy *= 0.5
        self.reproduction_cooldown = 100
        return Entity(self.x, self.y, genetics=self.genetics)

    def interact_with_nearby_entities(self, entities):
        interaction_radius = self.sense_radius * 1.5
        for other in entities:
            if other != self:
                distance = math.hypot(other.x - self.x, other.y - self.y)
                if distance < interaction_radius:
                    self._social_interaction(other)
                    self._share_knowledge(other)
                    
    def _social_interaction(self, other):
        # Create or update social bond
        if other not in self.social_bonds:
            self.social_bonds[other] = {
                'familiarity': 0.1,
                'trust': 0.5,
                'last_interaction': 0
            }
        
        bond = self.social_bonds[other]
        bond['familiarity'] = min(1.0, bond['familiarity'] + 0.01)
        bond['last_interaction'] = 0
        
        # Adjust trust based on mutual benefit
        if other.state == self.state:
            bond['trust'] = min(1.0, bond['trust'] + 0.02)
        
        # Form groups for mutual protection
        if bond['trust'] > 0.7 and self.state == "exploring":
            # Match direction and speed for group movement
            self.direction = (self.direction + other.direction) / 2
            self.speed = (self.speed + other.speed) / 2
            
    def _share_knowledge(self, other):
        if self.teaching_cooldown <= 0 and random.random() < self.social_disposition:
            # Share successful behaviors
            if len(self.learned_behaviors) > len(other.learned_behaviors):
                new_behavior = random.choice(list(self.learned_behaviors - other.learned_behaviors))
                other.learned_behaviors.add(new_behavior)
                self.teaching_cooldown = 50
                
            # Share genetic improvements
            if (self.success_count > other.success_count and 
                random.random() < self.social_disposition):
                shared_traits = self.genetics.share_traits(other.genetics)
                other.genetics.apply_shared_traits(shared_traits)
                
    def _update_social_bonds(self):
        # Age out old bonds
        bonds_to_remove = []
        for other, bond in self.social_bonds.items():
            bond['last_interaction'] += 1
            if bond['last_interaction'] > 500:  # Forget after long period
                bonds_to_remove.append(other)
        for other in bonds_to_remove:
            del self.social_bonds[other] 

    def is_alive(self):
        """Check if the entity is still alive based on energy and health."""
        return self.energy > MIN_ENERGY and self.health > 0 and self.age < MAX_AGE 