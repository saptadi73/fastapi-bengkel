"""
Auto-import all routers from routes directory.
This module automatically discovers and imports all route modules,
so you don't need to manually update main.py when adding new routes.
"""

import os
import importlib
from pathlib import Path

# List to store all routers
all_routers = []

# Get the directory where this __init__.py file is located
routes_dir = Path(__file__).parent

# Iterate through all Python files in the routes directory
for file in routes_dir.glob("routes_*.py"):
    # Get module name without .py extension
    module_name = file.stem
    
    try:
        # Import the module dynamically
        module = importlib.import_module(f"routes.{module_name}")
        
        # Check if the module has a 'router' attribute
        if hasattr(module, 'router'):
            all_routers.append(module.router)
            print(f"✓ Loaded router from: {module_name}")
        else:
            print(f"⚠ Warning: {module_name} does not have a 'router' attribute")
    
    except Exception as e:
        print(f"✗ Error loading {module_name}: {str(e)}")

print(f"\n📦 Total routers loaded: {len(all_routers)}")

# Export all_routers for use in main.py
__all__ = ['all_routers']
