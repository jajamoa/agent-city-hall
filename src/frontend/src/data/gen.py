import json
import math

def generate_sf_grid():
    # Define San Francisco boundaries
    bounds = {
        "north": 37.8120,
        "south": 37.7080,
        "east": -122.3549,
        "west": -122.5157
    }
    
    # Set grid cell size (in meters)
    cell_size = 100  # 100 meters

    cells = {}
    
    # Calculate lat/lng steps
    # 1 degree latitude equals approximately 111,000 meters
    lat_step = cell_size / 111000  # latitude step size
    
    # 1 degree longitude varies with latitude
    # Use center latitude to calculate longitude step
    center_lat = (bounds["north"] + bounds["south"]) / 2
    lng_step = cell_size / (111000 * math.cos(math.radians(center_lat)))  # longitude step size
    
    # Calculate number of grid cells needed
    lat_cells = int((bounds["north"] - bounds["south"]) / lat_step)
    lng_cells = int((bounds["east"] - bounds["west"]) / lng_step)
    
    for i in range(lat_cells):
        for j in range(lng_cells):
            # Calculate boundaries for each grid cell
            north = bounds["north"] - (i * lat_step)
            south = north - lat_step
            west = bounds["west"] + (j * lng_step)
            east = west + lng_step
            
            # Generate grid cell data
            cells[f"{i}_{j}"] = {
                "heightLimit": 0,
                "category": "residential",
                "lastUpdated": "2024-02-20",
                "bbox": {
                    "north": round(north, 6),
                    "south": round(south, 6),
                    "east": round(east, 6),
                    "west": round(west, 6)
                }
            }
    
    return {
        "gridConfig": {
            "cellSize": cell_size,
            "bounds": bounds
        },
        "heightLimits": {
            "default": 0,
            "options": [40, 65, 80, 85, 105, 130, 140, 240, 300]
        },
        "cells": cells
    }

if __name__ == "__main__":
    grid_data = generate_sf_grid()
    # Write the generated grid data to JSON file
    with open("sfZoningGrid2024.json", "w") as f:
        json.dump(grid_data, f, indent=2)
    print("Done")