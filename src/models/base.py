from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Basic configuration for opinion simulation models"""
    population: int = 30  # Number of agents to simulate

class BaseModel(ABC):
    """Base interface for all opinion simulation models"""
    
    def __init__(self, config: ModelConfig = None):
        """
        Initialize the model with configuration
        
        Args:
            config: Model configuration. If None, uses default configuration.
        """
        self.config = config or ModelConfig()
    
    @abstractmethod
    async def simulate_opinions(self, 
                              region: str,
                              proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate opinions for a given proposal in a region
        
        Args:
            region: Target region name
            proposal: Proposal details including title and description
            
        Returns:
            Opinion distribution summary
        """
        pass 