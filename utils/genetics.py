import random
import numpy as np
from utils.constants import *

class Genetics:
    def __init__(self, parent=None):
        self.generation = 0
        self.traits = {
            'speed': random.uniform(0.5, 2.0),
            'size': random.uniform(0.8, 1.2),
            'sense_radius': random.uniform(50, 150),
            'energy_efficiency': random.uniform(0.8, 1.2),
            'temperature_resistance': random.uniform(0.5, 1.5),
            'social_cohesion': random.uniform(0.0, 1.0),  # Tendency to stay near others
            'garden_attraction': random.uniform(0.0, 1.0),  # Tendency to seek and stay in gardens
            'teaching_ability': random.uniform(0.0, 1.0),  # Ability to teach others
            'learning_speed': random.uniform(0.0, 1.0),  # Speed of learning from others
            'garden_building_urge': random.uniform(0.0, 1.0),  # Tendency to build gardens
            'cooperation_level': random.uniform(0.0, 1.0)  # Willingness to cooperate
        }
        
        if parent:
            self.generation = parent.generation + 1
            self._inherit_traits(parent)
            self._mutate()
            
    def _inherit_traits(self, parent):
        for trait in self.traits:
            # Inherit with some variation
            self.traits[trait] = parent.traits[trait] * random.uniform(0.9, 1.1)
            
    def _mutate(self):
        # Higher mutation rate for social traits to encourage rapid evolution
        for trait in self.traits:
            if random.random() < 0.1:  # 10% chance of mutation
                if trait in ['social_cohesion', 'garden_attraction', 'teaching_ability', 
                           'learning_speed', 'garden_building_urge', 'cooperation_level']:
                    # More aggressive mutations for social traits
                    self.traits[trait] *= random.uniform(0.8, 1.2)
                else:
                    # Standard mutations for other traits
                    self.traits[trait] *= random.uniform(0.95, 1.05)
                    
    def get_trait(self, trait_name):
        return self.traits.get(trait_name, 1.0)
        
    def share_traits(self, other_genetics):
        """Share beneficial traits with another entity"""
        shared_traits = {}
        for trait in self.traits:
            if self.traits[trait] > other_genetics.traits[trait]:
                shared_traits[trait] = self.traits[trait] * 0.1  # Share 10% of the advantage
        return shared_traits
        
    def apply_shared_traits(self, shared_traits):
        """Apply shared traits from another entity"""
        for trait, value in shared_traits.items():
            self.traits[trait] = min(1.0, self.traits[trait] + value)
    
    def mutate(self):
        """Apply random mutations to traits"""
        for trait_name in self.traits:
            if trait_name != 'mutation_rate':  # Don't mutate mutation rate
                mutation = random.gauss(0, self.traits[trait_name] * self.traits['mutation_rate'])
                self.traits[trait_name] = max(0.1, self.traits[trait_name] + mutation)
    
    def crossover(self, other):
        """Create new genetics by combining traits from two parents"""
        child_traits = {}
        for trait_name in self.traits:
            # Randomly choose which parent's trait to inherit
            if random.random() < 0.5:
                child_traits[trait_name] = self.traits[trait_name]
            else:
                child_traits[trait_name] = other.traits[trait_name]
        
        # Create new genetics with combined traits
        child = Genetics()
        child.traits = child_traits
        child.mutate()  # Apply some mutations
        return child 