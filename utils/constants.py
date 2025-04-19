import pygame

# Display settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (100, 200, 255)

# Terrain types
TERRAIN_WATER = 0
TERRAIN_SAND = 1
TERRAIN_GRASS = 2
TERRAIN_ROCK = 3
TERRAIN_GARDEN = 4  # New! Regenerative garden tiles
TERRAIN_SPRING = 5  # New! Energy-boosting hot springs
TERRAIN_NEST = 6    # New! Safe resting spots

# Weather types
WEATHER_CLEAR = 0
WEATHER_RAIN = 1
WEATHER_SNOW = 2
WEATHER_STORM = 3

# Temperature range (Celsius)
TEMPERATURE_RANGE = (-10, 40)

# Entity settings
INITIAL_ENERGY = 100
MAX_ENERGY = 200
MIN_ENERGY = 10
ENERGY_DRAIN = 0.05  # Reduced from 0.1
REPRODUCTION_THRESHOLD = 80
REPRODUCTION_COST = 30
MAX_AGE = 2000  # Increased from 1000
HEALING_AMOUNT = 30
FEEDING_AMOUNT = 40
MAX_ENTITIES = 50
INITIAL_ENTITIES = 10
CARE_RADIUS = 50

# Body parts
BODY_PARTS = {
    'body': {'size': (8, 15), 'color': (200, 200, 200)},
    'head': {'size': (4, 8), 'color': (180, 180, 180)},
    'legs': {'size': (2, 4), 'color': (150, 150, 150)}
}

# Neural network parameters
INPUT_SIZE = 8
HIDDEN_SIZE = 16
OUTPUT_SIZE = 3
LEARNING_RATE = 0.01

# Genetic parameters
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.7

# Food parameters
FOOD_ENERGY_VALUE = 50
FOOD_SPAWN_RATE = 0.01  # Reduced from 0.02
FOOD_SIZE = 4
MAX_FOOD = 100
FOOD_LIFETIME = 2000  # Increased from 1000 to account for lower FPS
FOOD_DECAY_RATE = 0.05  # Reduced from 0.1
FOOD_SPAWN_RADIUS = 50
FOOD_QUALITY_RANGE = (0.5, 1.5)

# Garden parameters
GARDEN_SIZE = 30
GARDEN_GROWTH_RATE = 0.1  # Reduced from 0.15
GARDEN_MAX_FOOD = 15
GARDEN_ENERGY_BOOST = 0.5
MAX_GARDENS = 10

# New terrain effects
SPRING_HEAL_RATE = 0.5     # Health regeneration per tick in hot springs
NEST_ENERGY_SAVE = 0.5     # Energy drain reduction in nests
GARDEN_FOOD_BOOST = 2.0    # Multiplier for food value from garden tiles

# Entity states
HEALTHY_THRESHOLD = 70
WEAK_THRESHOLD = 30

# World settings
TERRAIN_SCALE = 0.1
FOOD_ENERGY = 50

# Simulation settings
SIMULATION_SPEED = 1.0

# Environmental effects
WEATHER_TYPES = ['clear', 'rain', 'snow']
WEATHER_EFFECTS = {
    'clear': {'speed_multiplier': 1.0, 'energy_drain': 1.0},
    'rain': {'speed_multiplier': 0.9, 'energy_drain': 1.2},
    'snow': {'speed_multiplier': 0.7, 'energy_drain': 1.5}
}

# Social behavior settings
SOCIAL_BOND_RADIUS = 100
SOCIAL_MEMORY_SIZE = 50
TEACHING_DURATION = 50
BOND_DECAY_RATE = 0.001
GROUP_COHESION = 0.7
KNOWLEDGE_SHARE_CHANCE = 0.3

# Learning parameters
LEARNING_RATE_RANGE = (0.05, 0.15)
MEMORY_DURATION = 500
SUCCESS_THRESHOLD = 0.5
BEHAVIOR_MUTATION_RATE = 0.1

# Group behavior settings
MIN_GROUP_SIZE = 2
MAX_GROUP_SIZE = 8
GROUP_SEPARATION = 30
GROUP_ALIGNMENT = 0.5
GROUP_COHESION_RADIUS = 80

# Cultural transmission
CULTURE_INHERITANCE_RATE = 0.8
INNOVATION_RATE = 0.1
TEACHING_EFFECTIVENESS = 0.7

# Safe zones
SAFE_ZONE_RADIUS = 100
SAFE_ZONE_HEALING = 0.2
SAFE_ZONE_ENERGY_BOOST = 0.3 