from typing import Dict, Type, Optional
from .base import BaseModel

class ModelRegistry:
    """
    Central registry for all available model implementations.
    Handles model registration and instantiation.
    """
    
    def __init__(self):
        """Initialize empty model registry"""
        self._models: Dict[str, Type[BaseModel]] = {}
    
    def register(self, model_class: Type[BaseModel]):
        """
        Register a new model implementation
        Args:
            model_class: The model class to register
        """
        instance = model_class()
        self._models[instance.model_name] = model_class
    
    def get_model(self, name: str, **kwargs) -> Optional[BaseModel]:
        """
        Get an instance of a registered model
        Args:
            name: Name of the model to instantiate
            **kwargs: Configuration parameters for the model
        Returns:
            BaseModel: Instantiated model if found, None otherwise
        """
        model_class = self._models.get(name)
        if model_class is None:
            return None
        return model_class(**kwargs)
    
    @property
    def available_models(self) -> list[str]:
        """
        Get list of all registered models
        Returns:
            list[str]: Names of available models
        """
        return list(self._models.keys())

# Global registry instance
registry = ModelRegistry() 