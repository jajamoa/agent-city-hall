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

async def validate_model_output(output: Dict[str, Any], population: int) -> bool:
    """
    Validate model output format and data consistency
    
    Args:
        output: Model output dictionary
        population: Expected number of agents
        
    Returns:
        bool: True if valid, raises exception if invalid
    """
    # 验证基本结构
    required_keys = {"summary", "comments", "key_themes"}
    if not all(key in output for key in required_keys):
        raise ValueError(f"Output must contain keys: {required_keys}")
    
    # 验证意见分布
    summary = output["summary"]
    required_stats = {"support", "oppose", "neutral"}
    if not all(key in summary for key in required_stats):
        raise ValueError(f"Summary must contain keys: {required_stats}")
    
    # 验证数值类型和范围
    if not all(isinstance(summary[key], int) for key in required_stats):
        raise ValueError("Summary statistics values must be integers")
    
    if not all(0 <= summary[key] <= 100 for key in required_stats):
        raise ValueError("Summary percentages must be between 0 and 100")
    
    # 验证总和为100
    total_percentage = sum(summary.values())
    if total_percentage != 100:
        raise ValueError(f"Summary percentages must sum to 100, got {total_percentage}")
    
    # 验证代理列表
    agents = output["comments"]
    if not isinstance(agents, list):
        raise ValueError("Comments must be a list")
    
    # 验证代理数量
    if len(agents) != population:
        raise ValueError(f"Number of agents ({len(agents)}) does not match population ({population})")
    
    # 验证代理字段
    required_agent_keys = {"id", "agent", "location", "cell_id", "opinion", "comment"}
    required_demographics = {"age", "income_level", "education_level", "occupation", "gender"}
    required_location_keys = {"lat", "lng"}
    
    # 验证ID唯一性
    agent_ids = set()
    actual_counts = {"support": 0, "oppose": 0, "neutral": 0}
    
    for agent in agents:
        # 验证基本字段
        if not all(key in agent for key in required_agent_keys):
            raise ValueError(f"Each agent must contain keys: {required_agent_keys}")
        
        # 验证ID唯一性
        if agent["id"] in agent_ids:
            raise ValueError(f"Duplicate agent ID: {agent['id']}")
        agent_ids.add(agent["id"])
        
        # 验证ID范围
        if not (1 <= agent["id"] <= population):
            raise ValueError(f"Agent ID must be between 1 and {population}")
        
        # 验证人口统计学字段
        if not all(key in agent["agent"] for key in required_demographics):
            raise ValueError(f"Each agent must have demographic attributes: {required_demographics}")
        
        # 验证人口统计学值的有效性
        demo = agent["agent"]
        if demo["age"] not in {"18-25", "26-40", "41-60", "60+"}:
            raise ValueError(f"Invalid age value: {demo['age']}")
        if demo["income_level"] not in {"low_income", "middle_income", "high_income"}:
            raise ValueError(f"Invalid income_level value: {demo['income_level']}")
        if demo["education_level"] not in {"high_school", "some_college", "bachelor", "postgraduate"}:
            raise ValueError(f"Invalid education_level value: {demo['education_level']}")
        if demo["occupation"] not in {"student", "white_collar", "service", "retired", "other"}:
            raise ValueError(f"Invalid occupation value: {demo['occupation']}")
        if demo["gender"] not in {"male", "female", "other"}:
            raise ValueError(f"Invalid gender value: {demo['gender']}")
        
        # 验证位置信息
        if not all(key in agent["location"] for key in required_location_keys):
            raise ValueError(f"Each agent must have location coordinates: {required_location_keys}")
        
        # 验证坐标值的类型和范围
        if not isinstance(agent["location"]["lat"], (int, float)):
            raise ValueError("Location latitude must be a number")
        if not isinstance(agent["location"]["lng"], (int, float)):
            raise ValueError("Location longitude must be a number")
        if not (-90 <= agent["location"]["lat"] <= 90):
            raise ValueError("Location latitude must be between -90 and 90")
        if not (-180 <= agent["location"]["lng"] <= 180):
            raise ValueError("Location longitude must be between -180 and 180")
        
        # 验证cell_id
        if not isinstance(agent["cell_id"], str):
            raise ValueError("Agent cell_id must be a string")
        if agent["cell_id"] not in SAMPLE_PROPOSAL["cells"]:
            raise ValueError(f"Invalid cell_id: {agent['cell_id']}")
        
        # 验证意见
        if agent["opinion"] not in {"support", "oppose", "neutral"}:
            raise ValueError("Agent opinion must be one of: support, oppose, neutral")
        actual_counts[agent["opinion"]] += 1
        
        # 验证评论
        if not isinstance(agent["comment"], str) or not agent["comment"]:
            raise ValueError("Agent comment must be a non-empty string")
    
    # 验证意见分布一致性
    for opinion in required_stats:
        expected_count = int(summary[opinion] * population / 100)
        actual_count = actual_counts[opinion]
        if abs(expected_count - actual_count) > 1:  # 允许1的误差（因为四舍五入）
            raise ValueError(f"Opinion count mismatch for {opinion}: "
                           f"summary shows {summary[opinion]}% ({expected_count} agents), "
                           f"but found {actual_count} agents")
    
    # 验证主题
    themes = output["key_themes"]
    if not isinstance(themes, dict) or not all(k in themes for k in ["support", "oppose"]):
        raise ValueError("key_themes must contain 'support' and 'oppose' lists")
    
    if not all(isinstance(themes[k], list) for k in ["support", "oppose"]):
        raise ValueError("Theme lists must be arrays")
    
    # 验证主题的存在性与意见分布的一致性
    if actual_counts["support"] > 0 and not themes["support"]:
        raise ValueError("Support themes missing when there are supporting agents")
    if actual_counts["oppose"] > 0 and not themes["oppose"]:
        raise ValueError("Opposition themes missing when there are opposing agents")
    
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
            proposal=SAMPLE_PROPOSAL
        )
        print("✓ Model simulation successful")
    except Exception as e:
        raise ValueError(f"Model simulation failed: {str(e)}")
    
    # Validate output format
    try:
        await validate_model_output(output, config.population)
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