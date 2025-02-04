import random
from typing import Dict, Any, List

class AgentGenerator:
    """Generate agents with random coordinates and demographics"""
    
    def __init__(self):
        """Initialize demographic options"""
        self.demographic_options = {
            "age": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
            "income": ["0-25000", "25000-50000", "50000-75000", "75000-100000", "100000+"],
            "education": ["high school", "some college", "bachelor's", "master's", "doctorate"],
            "occupation": ["student", "professional", "service", "retired", "other"],
            "gender": ["male", "female", "other"],
            "religion": ["christian", "jewish", "muslim", "buddhist", "hindu", "none", "other"],
            "race": ["white", "black", "asian", "hispanic", "other"]
        }
    
    def generate_agents(self, num_agents: int, grid_bounds: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate agents with random coordinates and demographics
        
        Args:
            num_agents: Number of agents to generate
            grid_bounds: Grid boundaries (north, south, east, west)
            
        Returns:
            List of agent dictionaries
        """
        agents = []
        for i in range(num_agents):
            # Generate random coordinates within bounds
            lat = random.uniform(grid_bounds["south"], grid_bounds["north"])
            lng = random.uniform(grid_bounds["west"], grid_bounds["east"])
            
            # Generate random demographics
            demographics = {
                attr: random.choice(options)
                for attr, options in self.demographic_options.items()
            }
            
            agents.append({
                "id": i,
                "coordinates": {
                    "lat": round(lat, 6),
                    "lng": round(lng, 6)
                },
                "agent": demographics
            })
        
        return agents 