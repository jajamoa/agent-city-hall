#!/usr/bin/env python3
import asyncio
import json
import importlib
from pathlib import Path
from typing import Type, Dict, Any
import argparse
# import sys
# sys.path.insert(0, r'G:\ACH\agent-city-hall\src')



from models.base import BaseModel, ModelConfig
from experiment.eval.utils.data_models import (
    ZoningProposal, EvaluationResult, Opinion,
    Agent, Comment, Location, OpinionSummary
)

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

def load_model_class(model_path: str) -> Type[BaseModel]:
    """
    Dynamically load model class from module path
    
    Args:
        model_path: Module path to model class (e.g. 'models.m01_basic.model.BasicSimulationModel')
        
    Returns:
        Type[BaseModel]: Model class
    """
    try:
        # Split path into module path and class name
        print("model path is", model_path)
        module_path, class_name = model_path.rsplit('.', 1)
        
        # Import module
        module = importlib.import_module(module_path)
        print(module)
        
        # Get class from module
        model_class = getattr(module, class_name)
        print(model_class)
        
        # Verify it's a BaseModel subclass
        if not issubclass(model_class, BaseModel):
            raise ValueError(f"Class {class_name} is not a subclass of BaseModel")
        
        return model_class
    except Exception as e:
        raise ValueError(f"Failed to load model class from {model_path}: {str(e)}")

# async def validate_model_output(output: Dict[str, Any], population: int) -> bool:
#     """Validate model output format and data consistency using Pydantic models."""
#     try:
#         # Validate basic structure using EvaluationResult model
#         result = EvaluationResult(
#             summary=OpinionSummary(**output["summary"]),
#             comments=[Comment(**c) for c in output["comments"]],
#             key_themes=output.get("key_themes")
#         )
        
#         # Only check if we have the correct number of comments
#         if len(result.comments) != population:
#             raise ValueError(f"Number of agents ({len(result.comments)}) does not match population ({population})")
        
#         return True
        
#     except Exception as e:
#         raise ValueError(f"Model output validation failed: {str(e)}")

async def validate_model_output(output: Dict[str, Any], population: int) -> bool:
    """Validate model output format and data consistency using Pydantic models."""
    try:
        # Validate basic structure using EvaluationResult model
        result = EvaluationResult(
            summary=OpinionSummary(**output["summary"]),
            comments=[Comment(**c) for c in output["comments"]],
            key_themes=output.get("key_themes")
        )
        
        # only check the comments
        if len(result.comments) == 0:
            raise ValueError("No agent opinions generated")
        
        return True
        
    except Exception as e:
        raise ValueError(f"Model output validation failed: {str(e)}")


async def validate_model(model_class: Type[BaseModel], config: ModelConfig = None) -> bool:
    """Validate a model implementation."""
    print(f"\nValidating model: {model_class.__name__}")
    
    try:
        # Validate input proposal
        proposal = ZoningProposal(**SAMPLE_PROPOSAL)
        print("✓ Sample proposal validation successful")
        
        # Test model initialization
        model = model_class(config)
        print("✓ Model initialization successful")
        
        # Test model simulation
        output = await model.simulate_opinions(
            region=SAMPLE_REGION,
            proposal=proposal.model_dump()
        )
        print("✓ Model simulation successful")
        
        # Validate output format
        await validate_model_output(output, config.population)
        print("✓ Model output format valid")
        
        print(f"Model {model_class.__name__} passed all validation checks!")
        return True
        
    except Exception as e:
        raise ValueError(f"Model validation failed: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description="Validate opinion simulation model implementation")
    parser.add_argument("--model-path", type=str, 
                       default="models.m01_basic.model.BasicSimulationModel",
                       help="Module path to model class")
    parser.add_argument("--population", type=int, default=30,
                       help="Number of agents to simulate")
    args = parser.parse_args()
    
    try:
        # Load model class
        model_class = load_model_class(args.model_path)
        print(f"Successfully loaded model class: {model_class.__name__}")
        
        # Create model config
        config = ModelConfig(population=args.population)
        
        # Validate model
        await validate_model(model_class, config)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 