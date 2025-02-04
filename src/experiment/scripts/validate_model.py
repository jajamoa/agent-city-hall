#!/usr/bin/env python3
import asyncio
import json
import importlib
from pathlib import Path
from typing import Type, Dict, Any
import argparse

from models.base import BaseModel, ModelConfig

SAMPLE_PROPOSAL = {
    "grid_config": {
        "cellSize": 100,
        "bounds": {
            "north": 37.8120,
            "south": 37.7080,
            "east": -122.3549,
            "west": -122.5157
        }
    },
    "height_limits": {
        "default": 40,
        "options": [40, 65, 80, 85, 105, 130, 140, 240, 300]
    },
    "cells": {
        "10_15": {
            "height_limit": 65,
            "category": "residential",
            "last_updated": "2024-03-15",
            "bbox": {
                "north": 37.7371,
                "south": 37.7261,
                "east": -122.4887,
                "west": -122.4997
            }
        }
    }
}

SAMPLE_REGION = "test_region"
SAMPLE_POPULATION = 3

def load_model_class(model_path: str) -> Type[BaseModel]:
    """
    Dynamically load model class from module path
    
    Args:
        model_path: Module path to model class (e.g. 'models.basic_simulation.model.BasicSimulationModel')
        
    Returns:
        Type[BaseModel]: Model class
    """
    try:
        # Split path into module path and class name
        module_path, class_name = model_path.rsplit('.', 1)
        
        # Import module
        module = importlib.import_module(module_path)
        
        # Get class from module
        model_class = getattr(module, class_name)
        
        # Verify it's a BaseModel subclass
        if not issubclass(model_class, BaseModel):
            raise ValueError(f"Class {class_name} is not a subclass of BaseModel")
        
        return model_class
    except Exception as e:
        raise ValueError(f"Failed to load model class from {model_path}: {str(e)}")

async def validate_model_output(output: tuple) -> bool:
    """
    Validate model output format
    
    Args:
        output: Model output tuple (opinion_distribution, sample_agents)
        
    Returns:
        bool: True if valid, raises exception if invalid
    """
    if not isinstance(output, tuple) or len(output) != 2:
        raise ValueError("Model output must be a tuple of (opinion_distribution, sample_agents)")
    
    opinion_distribution, sample_agents = output
    
    # Validate opinion distribution
    required_summary_keys = {"summary_statistics", "supporter_reasons", "opponent_reasons"}
    if not all(key in opinion_distribution for key in required_summary_keys):
        raise ValueError(f"Opinion distribution must contain keys: {required_summary_keys}")
    
    stats = opinion_distribution["summary_statistics"]
    required_stats = {"support", "oppose", "neutral"}
    if not all(key in stats for key in required_stats):
        raise ValueError(f"Summary statistics must contain keys: {required_stats}")
    
    if not all(isinstance(stats[key], int) for key in required_stats):
        raise ValueError("Summary statistics values must be integers")
    
    if sum(stats.values()) != SAMPLE_POPULATION:
        raise ValueError("Summary statistics total must equal input population")
    
    # Validate sample agents
    if not isinstance(sample_agents, list):
        raise ValueError("Sample agents must be a list")
    
    required_agent_keys = {"id", "agent", "opinion", "comment"}
    required_demographics = {"age", "income", "education", "occupation", "gender", "religion", "race"}
    
    for agent in sample_agents:
        if not all(key in agent for key in required_agent_keys):
            raise ValueError(f"Each agent must contain keys: {required_agent_keys}")
        
        if not all(key in agent["agent"] for key in required_demographics):
            raise ValueError(f"Each agent must have demographic attributes: {required_demographics}")
        
        if agent["opinion"] not in {"support", "oppose", "neutral"}:
            raise ValueError("Agent opinion must be one of: support, oppose, neutral")
        
        if not isinstance(agent["comment"], str):
            raise ValueError("Agent comment must be a string")
    
    return True

async def validate_model(model_class: Type[BaseModel], config: ModelConfig = None) -> bool:
    """
    Validate a model implementation
    
    Args:
        model_class: Model class to validate
        config: Optional model configuration
        
    Returns:
        bool: True if valid, raises exception if invalid
    """
    print(f"\nValidating model: {model_class.__name__}")
    
    # Test model initialization
    try:
        model = model_class(config)
        print("✓ Model initialization successful")
    except Exception as e:
        raise ValueError(f"Model initialization failed: {str(e)}")
    
    # Test model simulation
    try:
        output = await model.simulate_opinions(
            region=SAMPLE_REGION,
            population=SAMPLE_POPULATION,
            proposal=SAMPLE_PROPOSAL
        )
        print("✓ Model simulation successful")
    except Exception as e:
        raise ValueError(f"Model simulation failed: {str(e)}")
    
    # Validate output format
    try:
        await validate_model_output(output)
        print("✓ Model output format valid")
    except Exception as e:
        raise ValueError(f"Model output validation failed: {str(e)}")
    
    print(f"Model {model_class.__name__} passed all validation checks!")
    return True

async def main():
    parser = argparse.ArgumentParser(description="Validate opinion simulation model implementation")
    parser.add_argument("--model-path", type=str, 
                       default="models.m01_basic.model.BasicSimulationModel",
                       help="Module path to model class (e.g. 'models.m01_basic.model.BasicSimulationModel')")
    parser.add_argument("--num-samples", type=int, default=30,
                       help="Number of sample agents to generate")
    args = parser.parse_args()
    
    try:
        # Load model class
        model_class = load_model_class(args.model_path)
        print(f"Successfully loaded model class: {model_class.__name__}")
        
        # Create model config
        config = ModelConfig(num_sample_agents=args.num_samples)
        
        # Validate model
        await validate_model(model_class, config)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 