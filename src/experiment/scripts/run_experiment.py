#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
import os
from datetime import datetime

from models.base import BaseModel, ModelConfig
from models.m01_basic.model import BasicSimulationModel
from models.m02_stupid.model import StupidAgentModel

AVAILABLE_MODELS = {
    "basic": BasicSimulationModel,
    "stupid": StupidAgentModel
}

DEFAULT_REGION = "san_francisco"

def get_project_root() -> Path:
    """Get the absolute path of the project root directory"""
    current_file = Path(__file__).resolve()
    # Search upwards from current file until finding the project root
    for parent in [current_file, *current_file.parents]:
        if (parent / 'src').exists():
            return parent
    raise RuntimeError("Could not find project root directory")

async def load_proposals(input_dir: str) -> List[Dict[str, Any]]:
    """Load all proposals from input directory"""
    proposals = []
    input_path = Path(input_dir)
    for file_path in sorted(input_path.glob("*.json")):
        with open(file_path) as f:
            data = json.load(f)
            proposals.append(data)
    return proposals

async def save_results(output_dir: str, exp_id: str, proposal_id: str, proposal: Dict[str, Any], opinion_distribution: Dict[str, Any]):
    """Save experiment results to output directory"""
    output_path = Path(output_dir) / exp_id
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存输入提案
    with open(output_path / f"{proposal_id}_input.json", "w") as f:
        json.dump(proposal, f, indent=2)
    
    # 保存模拟结果
    with open(output_path / f"{proposal_id}_output.json", "w") as f:
        json.dump(opinion_distribution, f, indent=2)

async def main():
    # Get project root
    project_root = get_project_root()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run zoning proposal evaluation experiment")
    parser.add_argument("--input-dir", type=str, 
                       default=str(project_root / "src/experiment/eval/data/inputs/proposals"),
                       help="Directory containing input proposals")
    parser.add_argument("--output-dir", type=str, 
                       default=str(project_root / "src/experiment/log"),
                       help="Base directory for experiment outputs")
    parser.add_argument("--model", type=str, default="stupid",
                       choices=list(AVAILABLE_MODELS.keys()),
                       help="Model to use")
    parser.add_argument("--population", type=int, default=30,
                       help="Number of agents to simulate")
    parser.add_argument("--name", type=str, required=True,
                       help="Experiment name")
    args = parser.parse_args()
    
    # Load proposals
    proposals = await load_proposals(args.input_dir)
    print(f"Loaded {len(proposals)} proposals")
    
    # Initialize model
    model_class = AVAILABLE_MODELS[args.model]
    config = ModelConfig(population=args.population)
    model = model_class(config)
    
    # Create experiment ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_id = f"{args.name}_{args.model}_{timestamp}"
    
    # Run experiment
    print(f"\nRunning experiment: {exp_id}")
    print(f"Model: {args.model}")
    print(f"Number of proposals: {len(proposals)}")
    print(f"Population size: {args.population}")
    
    for i, proposal in enumerate(proposals):
        proposal_id = f"proposal_{i:03d}"
        print(f"\nProcessing {proposal_id}...")
        
        try:
            # Run simulation
            opinion_distribution = await model.simulate_opinions(
                region=DEFAULT_REGION,
                proposal=proposal
            )
            
            # Save results
            await save_results(args.output_dir, exp_id, proposal_id, proposal, opinion_distribution)
            print(f"✓ Results saved")
            print(f"  - Input: {proposal_id}_input.json")
            print(f"  - Output: {proposal_id}_output.json")
            
        except Exception as e:
            print(f"Error processing {proposal_id}: {str(e)}")
    
    print(f"\nExperiment completed: {exp_id}")
    print(f"Results saved in: {args.output_dir}/{exp_id}")

if __name__ == "__main__":
    asyncio.run(main()) 