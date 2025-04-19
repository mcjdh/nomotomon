import random
import math
from utils.constants import *

class SocialBehavior:
    def __init__(self):
        self.behaviors = set()
        self.innovations = []
        self.cultural_memory = []
        
    @staticmethod
    def calculate_group_center(entities):
        if not entities:
            return None
        x_sum = sum(e.x for e in entities)
        y_sum = sum(e.y for e in entities)
        return (x_sum / len(entities), y_sum / len(entities))
    
    @staticmethod
    def calculate_group_direction(entities):
        if not entities:
            return 0
        return sum(e.direction for e in entities) / len(entities)
    
    def form_groups(self, entities):
        groups = []
        ungrouped = set(entities)
        
        while ungrouped and len(groups) < len(entities) / MIN_GROUP_SIZE:
            seed = random.choice(list(ungrouped))
            group = {seed}
            ungrouped.remove(seed)
            
            # Find nearby entities that could join the group
            for entity in list(ungrouped):
                if len(group) >= MAX_GROUP_SIZE:
                    break
                    
                # Check if entity is close to the group center
                center = self.calculate_group_center(group)
                dist = math.hypot(entity.x - center[0], entity.y - center[1])
                
                if dist < GROUP_COHESION_RADIUS:
                    group.add(entity)
                    ungrouped.remove(entity)
            
            if len(group) >= MIN_GROUP_SIZE:
                groups.append(group)
        
        return groups
    
    def update_group_behavior(self, group):
        center = self.calculate_group_center(group)
        avg_direction = self.calculate_group_direction(group)
        
        for entity in group:
            # Separation: avoid crowding
            separation = [0, 0]
            for other in group:
                if other != entity:
                    dx = entity.x - other.x
                    dy = entity.y - other.y
                    dist = math.hypot(dx, dy)
                    if dist < GROUP_SEPARATION:
                        separation[0] += dx / dist
                        separation[1] += dy / dist
            
            # Alignment: match group direction
            direction_diff = (avg_direction - entity.direction) % (2 * math.pi)
            if direction_diff > math.pi:
                direction_diff -= 2 * math.pi
            entity.direction += direction_diff * GROUP_ALIGNMENT
            
            # Cohesion: move toward center
            if center:
                to_center_x = center[0] - entity.x
                to_center_y = center[1] - entity.y
                dist_to_center = math.hypot(to_center_x, to_center_y)
                if dist_to_center > GROUP_COHESION_RADIUS:
                    entity.direction = math.atan2(to_center_y, to_center_x)
    
    def share_culture(self, entity1, entity2):
        if random.random() < KNOWLEDGE_SHARE_CHANCE:
            # Share learned behaviors
            if entity1.learned_behaviors and entity2.learned_behaviors:
                behavior = random.choice(list(entity1.learned_behaviors))
                if random.random() < TEACHING_EFFECTIVENESS:
                    entity2.learned_behaviors.add(behavior)
                    
            # Share innovations
            if entity1.success_count > entity2.success_count:
                if random.random() < INNOVATION_RATE:
                    innovation = {
                        'behavior': random.choice(list(entity1.learned_behaviors)),
                        'success_rate': entity1.success_count / (entity1.age + 1)
                    }
                    self.innovations.append(innovation)
    
    def create_safe_zone(self, x, y, entities):
        """Create a temporary safe zone for group gatherings"""
        for entity in entities:
            dist = math.hypot(entity.x - x, entity.y - y)
            if dist < SAFE_ZONE_RADIUS:
                # Heal and energize entities in safe zone
                entity.health += SAFE_ZONE_HEALING
                entity.energy = min(MAX_ENERGY, 
                                  entity.energy + SAFE_ZONE_ENERGY_BOOST)
                
                # Increase learning rate temporarily
                entity.learning_rate *= 1.2
                
    def update_cultural_memory(self):
        """Update and maintain cultural memory of successful behaviors"""
        # Sort innovations by success rate
        self.innovations.sort(key=lambda x: x['success_rate'], reverse=True)
        
        # Keep only the best innovations
        self.innovations = self.innovations[:SOCIAL_MEMORY_SIZE]
        
        # Decay old memories
        self.cultural_memory = [mem for mem in self.cultural_memory 
                              if random.random() > BOND_DECAY_RATE] 