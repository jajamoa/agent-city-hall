from typing import Dict, Any
import random

from ..base import BaseModel, ModelConfig

class TemplateModel(BaseModel):
    """Template for opinion simulation model implementation"""
    
    def __init__(self, config: ModelConfig = None):
        """Initialize model components"""
        super().__init__(config)
        # Initialize your model components here
    
    async def simulate_opinions(self,
                              region: str,
                              proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate opinions for a given proposal
        
        Args:
            region: Target region name
            proposal: Proposal details including grid configuration and rezoning cells
            
        Returns:
            Opinion distribution summary with agent details
        """
        # Get grid bounds from proposal
        grid_bounds = (proposal.get("grid_config", {})
                      .get("bounds", {
                          "north": 37.8120,
                          "south": 37.7080,
                          "east": -122.3549,
                          "west": -122.5157
                      }))
        
        # Generate sample agents
        agents = []
        opinion_counts = {"support": 0, "oppose": 0, "neutral": 0}
        
        # Example demographic options
        demographics = {
            "age": ["18-25", "26-40", "41-60", "60+"],
            "income_level": ["low_income", "middle_income", "high_income"],
            "education_level": ["high_school", "some_college", "bachelor", "postgraduate"],
            "occupation": ["student", "white_collar", "service", "retired", "other"],
            "gender": ["male", "female", "other"]
        }
        
        # Generate agents based on configured population
        for i in range(self.config.population):
            # Random location within bounds
            lat = random.uniform(grid_bounds["south"], grid_bounds["north"])
            lng = random.uniform(grid_bounds["west"], grid_bounds["east"])
            
            # Find nearest cell
            nearest_cell_id = None
            min_distance = float('inf')
            
            for cell_id, cell in proposal['cells'].items():
                bbox = cell['bbox']
                cell_lat = (bbox['north'] + bbox['south']) / 2
                cell_lng = (bbox['east'] + bbox['west']) / 2
                
                distance = ((lat - cell_lat) ** 2 + (lng - cell_lng) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    nearest_cell_id = cell_id
            
            # Random demographics and opinion
            agent = {
                "id": i + 1,
                "agent": {
                    "age": random.choice(demographics["age"]),
                    "income_level": random.choice(demographics["income_level"]),
                    "education_level": random.choice(demographics["education_level"]),
                    "occupation": random.choice(demographics["occupation"]),
                    "gender": random.choice(demographics["gender"])
                },
                "location": {
                    "lat": lat,
                    "lng": lng
                },
                "cell_id": nearest_cell_id,
                "opinion": random.choice(["support", "oppose", "neutral"]),
                "comment": "This is a sample comment."  # In real implementation, generate meaningful comments
            }
            
            agents.append(agent)
            opinion_counts[agent["opinion"]] += 1
        
        # Example themes
        themes = {
            "support": ["housing needs", "urban development", "economic growth"],
            "oppose": ["traffic concerns", "shadow impact", "density issues"]
        }
        
        # Return results ensuring all numbers match
        return {
            "summary": {
                "support": int(opinion_counts["support"] * 100 / self.config.population),
                "oppose": int(opinion_counts["oppose"] * 100 / self.config.population),
                "neutral": 100 - int(opinion_counts["support"] * 100 / self.config.population) - 
                          int(opinion_counts["oppose"] * 100 / self.config.population)
            },
            "comments": agents,
            "key_themes": {
                "support": themes["support"] if opinion_counts["support"] > 0 else [],
                "oppose": themes["oppose"] if opinion_counts["oppose"] > 0 else []
            }
        } 