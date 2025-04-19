import os
import sys
import pygame
import random
import traceback
from pygame.locals import *

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from entities.entity import Entity
from world.world import World
from utils.constants import *

def draw_graph(surface, data, x, y, width, height, color, max_value=None):
    if not data:
        return
    
    if max_value is None:
        max_value = max(data)
    
    # Draw background
    pygame.draw.rect(surface, (30, 30, 30), (x, y, width, height))
    
    # Draw graph
    points = []
    for i, value in enumerate(data[-width:]):
        points.append((
            x + i,
            y + height - (value / max_value * height)
        ))
    
    if len(points) > 1:
        pygame.draw.lines(surface, color, False, points)

def initialize_pygame():
    try:
        pygame.init()
        pygame.font.init()
        return True
    except Exception as e:
        print(f"Failed to initialize Pygame: {e}")
        return False

def create_display():
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Nomotomon - Life Simulator')
        return screen
    except Exception as e:
        print(f"Failed to create display: {e}")
        return None

def draw_ui(screen, world):
    # Create UI surface with transparency
    ui_surface = pygame.Surface((200, 150), pygame.SRCALPHA)
    pygame.draw.rect(ui_surface, (0, 0, 0, 128), ui_surface.get_rect())
    
    # Prepare text
    font = pygame.font.Font(None, 24)
    texts = [
        f"Time: {world.environment.time_of_day:02d}:00",
        f"Season: {['Spring', 'Summer', 'Fall', 'Winter'][world.environment.season]}",
        f"Weather: {['Clear', 'Rain', 'Snow', 'Storm'][world.environment.weather]}",
        f"Temp: {world.environment.temperature:.1f}°C",
        f"Entities: {len(world.entities)}",
        f"Food: {len(world.food)}"
    ]
    
    # Draw text
    for i, text in enumerate(texts):
        text_surface = font.render(text, True, (255, 255, 255))
        ui_surface.blit(text_surface, (10, 10 + i * 25))
    
    # Draw UI in top-right corner
    screen.blit(ui_surface, (WINDOW_WIDTH - 210, 10))
    
    # Draw selected entity info if any
    if world.selected_entity:
        entity = world.selected_entity
        entity_ui = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(entity_ui, (0, 0, 0, 128), entity_ui.get_rect())
        
        entity_texts = [
            f"Species: {entity.species_name}",
            f"Gen: {entity.generation}",
            f"Energy: {int(entity.energy)}",
            f"Health: {int(entity.health)}",
            f"Age: {entity.age}",
            f"State: {entity.state}",
            f"Success: {(entity.success_count/max(1, entity.age)):.1%}"
        ]
        
        for i, text in enumerate(entity_texts):
            text_surface = font.render(text, True, (255, 255, 255))
            entity_ui.blit(text_surface, (10, 10 + i * 25))
        
        screen.blit(entity_ui, (10, 10))

def main():
    if not initialize_pygame():
        return
    
    screen = create_display()
    if not screen:
        pygame.quit()
        return
        
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    try:
        # Create world
        world = World()
        
        # Add initial entities
        for _ in range(min(INITIAL_ENTITIES, MAX_ENTITIES)):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            world.add_entity(x, y)
            
        # Statistics
        population_history = []
        energy_history = []
        health_history = []
        success_rate_history = []
        learning_progress = []
        
        # Main game loop
        running = True
        paused = False
        show_help = True
        show_graphs = True
        frame_counter = 0
        
        while running:
            try:
                # Handle events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            running = False
                        elif event.key == K_SPACE:
                            paused = not paused
                        elif event.key == K_r:  # Reset simulation
                            world = World()
                            for _ in range(min(INITIAL_ENTITIES, MAX_ENTITIES)):
                                x = random.randint(0, WINDOW_WIDTH)
                                y = random.randint(0, WINDOW_HEIGHT)
                                world.add_entity(x, y)
                            # Reset statistics
                            population_history = []
                            energy_history = []
                            health_history = []
                            success_rate_history = []
                            learning_progress = []
                        elif event.key == K_h:  # Heal selected entity
                            world.heal_selected_entity()
                        elif event.key == K_f:  # Feed entities near mouse
                            x, y = pygame.mouse.get_pos()
                            world.feed_nearby_entities(x, y)
                        elif event.key == K_g:  # Place garden
                            x, y = pygame.mouse.get_pos()
                            world.add_garden(x, y)
                        elif event.key == K_TAB:  # Toggle help
                            show_help = not show_help
                        elif event.key == K_s:  # Toggle statistics graphs
                            show_graphs = not show_graphs
                    elif event.type == MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if event.button == 1:  # Left click
                            world.add_entity(x, y)
                        elif event.button == 3:  # Right click
                            world.select_entity_at(x, y)
                
                if not paused:
                    # Update world
                    world.update()
                    
                    # Record statistics every 10 frames
                    frame_counter += 1
                    if frame_counter % 10 == 0:
                        population_history.append(len(world.entities))
                        if len(population_history) > 300:
                            population_history.pop(0)
                        
                        if world.entities:
                            # Calculate averages
                            avg_energy = sum(e.energy for e in world.entities) / len(world.entities)
                            avg_health = sum(e.health for e in world.entities) / len(world.entities)
                            avg_success = sum(e.success_count / max(1, e.age) for e in world.entities) / len(world.entities)
                            
                            energy_history.append(avg_energy)
                            health_history.append(avg_health)
                            success_rate_history.append(avg_success * 100)
                            
                            if len(energy_history) > 300:
                                energy_history.pop(0)
                            if len(health_history) > 300:
                                health_history.pop(0)
                            if len(success_rate_history) > 300:
                                success_rate_history.pop(0)
                
                # Draw everything
                screen.fill(BLACK)
                world.draw(screen)
                
                # Draw UI
                draw_ui(screen, world)
                
                # Draw graphs if enabled
                if show_graphs and (population_history or energy_history):
                    graph_width = 200
                    graph_height = 100
                    graph_x = WINDOW_WIDTH - graph_width - 10
                    
                    # Population graph
                    draw_graph(screen, population_history, graph_x, 170, 
                             graph_width, graph_height, (0, 255, 0), MAX_ENTITIES)
                    text = font.render("Population", True, (0, 255, 0))
                    screen.blit(text, (graph_x, 275))
                    
                    # Energy graph
                    draw_graph(screen, energy_history, graph_x, 300,
                             graph_width, graph_height, (255, 255, 0), MAX_ENERGY)
                    text = font.render("Energy", True, (255, 255, 0))
                    screen.blit(text, (graph_x, 405))
                    
                    # Health graph
                    draw_graph(screen, health_history, graph_x, 430,
                             graph_width, graph_height, (255, 0, 0), 100)
                    text = font.render("Health", True, (255, 0, 0))
                    screen.blit(text, (graph_x, 535))
                
                if show_help:
                    controls = [
                        "Controls:",
                        "Left Click: Add entity",
                        "Right Click: Select entity",
                        "G: Place garden",
                        "H: Heal selected",
                        "F: Feed nearby",
                        "Space: Pause",
                        "S: Toggle graphs",
                        "R: Reset",
                        "Tab: Toggle help",
                        "Esc: Quit"
                    ]
                    
                    help_x = 10
                    help_y = WINDOW_HEIGHT - len(controls) * 25 - 10
                    help_surface = pygame.Surface((200, len(controls) * 25 + 20), pygame.SRCALPHA)
                    pygame.draw.rect(help_surface, (0, 0, 0, 128), help_surface.get_rect())
                    
                    for i, control in enumerate(controls):
                        text = font.render(control, True, WHITE)
                        help_surface.blit(text, (10, 10 + i * 25))
                    
                    screen.blit(help_surface, (help_x, help_y))
                
                # Update display
                pygame.display.flip()
                clock.tick(FPS)
                
            except Exception as e:
                print(f"Error in game loop: {e}")
                traceback.print_exc()
                running = False
                
    except Exception as e:
        print(f"Error in main: {e}")
        traceback.print_exc()
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 