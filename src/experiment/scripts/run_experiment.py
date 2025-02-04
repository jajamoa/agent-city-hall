#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
from datetime import datetime

from models.base import BaseModel, ModelConfig
from models.m01_basic.model import BasicSimulationModel
from models.m02_stupid.model import StupidAgentModel
from experiment.eval.utils.data_models import ZoningProposal, EvaluationResult
from experiment.eval.utils.data_manager import DataManager

AVAILABLE_MODELS = {
    "basic": BasicSimulationModel,
    "stupid": StupidAgentModel
}

DEFAULT_REGION = "san_francisco"

def get_project_root() -> Path:
    """Get the absolute path of the project root directory."""
    current_file = Path(__file__).resolve()
    for parent in [current_file, *current_file.parents]:
        if (parent / 'src').exists():
            return parent
    raise RuntimeError("Could not find project root directory")

async def main():
    # Get project root
    project_root = get_project_root()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run zoning proposal evaluation experiment")
    parser.add_argument("--name", type=str, required=True,
                       help="Experiment name")
    parser.add_argument("--model", type=str, default="stupid",
                       choices=list(AVAILABLE_MODELS.keys()),
                       help="Model to use")
    parser.add_argument("--population", type=int, default=30,
                       help="Number of agents to simulate")
    args = parser.parse_args()
    
    # Initialize data manager and create experiment directory
    data_manager = DataManager(base_dir=str(project_root / "src/experiment"))
    exp_dir, exp_id = data_manager.create_experiment(args.name, args.model)
    
    # Load proposals
    proposals = []
    for file_path in sorted(data_manager.inputs_dir.glob("*.json")):
        with open(file_path) as f:
            data = json.load(f)
            proposals.append(ZoningProposal.model_validate(data))
    print(f"Loaded {len(proposals)} proposals")
    
    # Initialize model
    model_class = AVAILABLE_MODELS[args.model]
    config = ModelConfig(population=args.population)
    model = model_class(config)
    
    # Run experiment
    print(f"\nRunning experiment: {exp_id}")
    print(f"Model: {args.model}")
    print(f"Number of proposals: {len(proposals)}")
    print(f"Population size: {args.population}")
    
    start_time = datetime.now()
    
    for i, proposal in enumerate(proposals):
        proposal_id = f"proposal_{i:03d}"
        print(f"\nProcessing {proposal_id}...")
        
        try:
            # Run simulation
            opinion_distribution = await model.simulate_opinions(
                region=DEFAULT_REGION,
                proposal=proposal.model_dump()
            )
            
            # Save result
            result = EvaluationResult.model_validate(opinion_distribution)
            data_manager.save_experiment_result(
                exp_dir=exp_dir,
                proposal=proposal,
                result=result,
                proposal_id=proposal_id,
                model_name=args.model
            )
            print(f"✓ Results saved for {proposal_id}")
            
        except Exception as e:
            print(f"Error processing {proposal_id}: {str(e)}")
    
    # Save experiment metadata
    end_time = datetime.now()
    data_manager.save_metadata(
        exp_dir=exp_dir,
        args=args,
        start_time=start_time,
        end_time=end_time,
        additional_info={
            "region": DEFAULT_REGION,
            "num_proposals": len(proposals)
        }
    )
    
    print(f"\nExperiment completed: {exp_id}")
    print(f"Duration: {(end_time - start_time).total_seconds():.2f} seconds")
    print(f"Results saved in: {data_manager.log_dir}/{exp_id}")

if __name__ == "__main__":
    asyncio.run(main()) 