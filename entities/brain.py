import numpy as np
import random
from utils.constants import *

class NeuralNetwork:
    def __init__(self, parent=None):
        self.species_name = self._generate_species_name()
        self.weights = self._initialize_weights() if not parent else self._inherit_weights(parent)
        self.memory = []  # Store recent experiences
        self.social_memory = {}  # Store interactions with other entities
        self.learned_behaviors = set()  # Store successful behaviors
        
    def _initialize_weights(self):
        # Enhanced input layer for social behaviors
        input_size = 14  # Match actual number of inputs
        hidden_size = 32  # Increased hidden layer size
        output_size = 6  # Added garden building output
        
        # Initialize weights with Xavier/Glorot initialization
        weights = {
            'input_hidden': np.random.randn(input_size, hidden_size) * np.sqrt(2.0 / input_size),
            'hidden_output': np.random.randn(hidden_size, output_size) * np.sqrt(2.0 / hidden_size)
        }
        return weights
        
    def _inherit_weights(self, parent):
        weights = {}
        for layer in parent.weights:
            weights[layer] = parent.weights[layer].copy()
            # Add some mutation to weights
            mutation = np.random.normal(0, 0.1, weights[layer].shape)
            weights[layer] += mutation
        return weights
        
    def think(self, inputs):
        # Forward propagation with just the inputs (no social context for now)
        hidden = np.tanh(np.dot(inputs, self.weights['input_hidden']))
        outputs = np.tanh(np.dot(hidden, self.weights['hidden_output']))
        
        # Interpret outputs
        return {
            'speed_multiplier': (outputs[0] + 1) / 2,  # Normalize to [0, 1]
            'direction_change': outputs[1] * 0.2,  # Scale down direction changes
            'reproduction_urge': (outputs[2] + 1) / 2,
            'grid_movement': outputs[3],
            'social_interaction': (outputs[4] + 1) / 2,
            'garden_building': (outputs[5] + 1) / 2
        }
        
    def _get_social_context(self):
        # Calculate social context based on recent interactions
        social_cohesion = 0.0
        teaching_ability = 0.0
        learning_speed = 0.0
        cooperation_level = 0.0
        
        if self.memory:
            # Calculate average social metrics from recent memory
            recent_memory = self.memory[-10:]  # Last 10 experiences
            for experience in recent_memory:
                if 'social' in experience:
                    social_cohesion += experience['social']['cohesion']
                    teaching_ability += experience['social']['teaching']
                    learning_speed += experience['social']['learning']
                    cooperation_level += experience['social']['cooperation']
                    
            # Normalize
            social_cohesion /= len(recent_memory)
            teaching_ability /= len(recent_memory)
            learning_speed /= len(recent_memory)
            cooperation_level /= len(recent_memory)
            
        return np.array([
            social_cohesion,
            teaching_ability,
            learning_speed,
            cooperation_level,
            len(self.learned_behaviors) / 10.0,  # Normalize to [0, 1]
            len(self.social_memory) / 20.0  # Normalize to [0, 1]
        ])
        
    def learn(self, experience):
        # Store experience in memory
        self.memory.append(experience)
        if len(self.memory) > 100:  # Limit memory size
            self.memory.pop(0)
            
        # Update weights using backpropagation
        inputs = np.array(experience['inputs'])
        targets = np.array(experience['outputs'])
        reward = experience['reward']
        
        # Forward pass
        hidden = np.tanh(np.dot(inputs, self.weights['input_hidden']))
        outputs = np.tanh(np.dot(hidden, self.weights['hidden_output']))
        
        # Calculate error
        error = targets - outputs
        
        # Backpropagate error
        learning_rate = 0.01 * reward  # Scale learning by reward
        hidden_error = np.dot(error, self.weights['hidden_output'].T)
        
        # Update weights
        self.weights['hidden_output'] += learning_rate * np.outer(hidden, error)
        self.weights['input_hidden'] += learning_rate * np.outer(inputs, hidden_error)
        
        # Store successful behaviors
        if reward > 0.5:  # If behavior was successful
            behavior_hash = hash(tuple(experience['inputs']))
            self.learned_behaviors.add(behavior_hash)
            
    def _generate_species_name(self):
        # Generate a unique species name
        prefixes = ['Nomoto', 'Mono', 'Tomo', 'Komo', 'Lomo']
        suffixes = ['mon', 'ton', 'don', 'kon', 'lon']
        return random.choice(prefixes) + random.choice(suffixes)

    def get_genetic_code(self):
        return {
            'weights': self.weights,
            'species_name': self.species_name,
            'social_memory': self.social_memory,
            'learned_behaviors': list(self.learned_behaviors)
        } 