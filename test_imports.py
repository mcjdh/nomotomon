import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

try:
    from utils.constants import *
    print("Successfully imported constants")
    
    from utils.genetics import Genetics
    print("Successfully imported Genetics")
    
    from environment.environment import Environment
    print("Successfully imported Environment")
    
    from entities.entity import Entity
    print("Successfully imported Entity")
    
    from world.world import World
    print("Successfully imported World")
    
    print("\nAll imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Project root: {project_root}") 