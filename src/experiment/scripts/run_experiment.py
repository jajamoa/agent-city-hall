#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
import argparse
from datetime import datetime
import yaml

from models.base import BaseModel, ModelConfig
from models.m01_basic.model import BasicSimulationModel
from models.m02_stupid.model import StupidAgentModel
from experiment.eval.utils.data_models import ZoningProposal, EvaluationResult
from experiment.eval.utils.data_manager import DataManager

AVAILABLE_MODELS = {
    "basic": BasicSimulationModel,
    "stupid": StupidAgentModel
}

def get_project_root() -> Path:
    """Get the absolute path of the project root directory."""
    current_file = Path(__file__).resolve()
    for parent in [current_file, *current_file.parents]:
        if (parent / 'src').exists():
            return parent
    raise RuntimeError("Could not find project root directory")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run experiment with protocol")
    parser.add_argument(
        "--protocol",
        type=str,
        required=True,
        help="Path to experiment protocol YAML file"
    )
    return parser.parse_args()

def load_protocol(protocol_path: str) -> dict:
    """Load experiment protocol from YAML file."""
    with open(protocol_path) as f:
        protocol = yaml.safe_load(f)
    return protocol

async def run_experiment(protocol: dict):
    """Run experiment based on protocol."""
    # Get project root
    project_root = get_project_root()
    
    # Initialize data manager and create experiment directory
    data_manager = DataManager(base_dir=str(project_root / "src/experiment"))
    exp_dir, exp_id = data_manager.create_experiment(protocol["name"], protocol["model"])
    
    # Save protocol for reproducibility
    with open(exp_dir / "protocol.yaml", "w") as f:
        yaml.dump(protocol, f, default_flow_style=False)
    
    # Initialize model
    model_class = AVAILABLE_MODELS[protocol["model"]]
    config = ModelConfig(population=protocol["population"])
    model = model_class(config)
    
    # Run experiment
    print(f"\nRunning experiment: {exp_id}")
    print(f"Model: {protocol['model']}")
    print(f"Population size: {protocol['population']}")
    print(f"Number of proposals: {len(protocol['input']['proposals'])}")
    
    start_time = datetime.now()
    
    for i, proposal_file in enumerate(protocol["input"]["proposals"]):
        proposal_id = f"proposal_{i:03d}"
        print(f"\nProcessing {proposal_id} ({proposal_file})...")
        
        try:
            # Load proposal
            input_file = data_manager.inputs_dir / proposal_file
            with open(input_file) as f:
                data = json.load(f)
                proposal = ZoningProposal.model_validate(data)
            
            # Run simulation
            opinion_distribution = await model.simulate_opinions(
                region=protocol.get("region", "san_francisco"),
                proposal=proposal.model_dump()
            )
            
            # Save result
            result = EvaluationResult.model_validate(opinion_distribution)
            data_manager.save_experiment_result(
                exp_dir=exp_dir,
                proposal=proposal,
                result=result,
                proposal_id=proposal_id,
                model_name=protocol["model"]
            )
            print(f"✓ Results saved for {proposal_id}")
            
        except Exception as e:
            print(f"Error processing {proposal_id}: {str(e)}")
    
    # Save experiment metadata
    end_time = datetime.now()
    protocol["runtime"] = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds()
    }
    data_manager.save_metadata(
        exp_dir=exp_dir,
        args=protocol,
        start_time=start_time,
        end_time=end_time
    )
    
    print(f"\nExperiment completed: {exp_id}")
    print(f"Duration: {(end_time - start_time).total_seconds():.2f} seconds")
    print(f"Results saved in: {data_manager.log_dir}/{exp_id}")

async def main():
    args = parse_args()
    protocol = load_protocol(args.protocol)
    await run_experiment(protocol)

if __name__ == "__main__":
    asyncio.run(main()) 