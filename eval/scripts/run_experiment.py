#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from typing import List
import argparse

from eval.src.models.gpt4 import GPT4Model
from eval.src.evaluator import Evaluator
from eval.src.schemas import ZoningProposal

async def load_proposals(input_dir: str) -> List[ZoningProposal]:
    """Load all proposals from input directory"""
    proposals = []
    input_path = Path(input_dir)
    for file_path in sorted(input_path.glob("*.json")):
        with open(file_path) as f:
            data = json.load(f)
            proposals.append(ZoningProposal.model_validate(data))
    return proposals

async def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run zoning proposal evaluation experiment")
    parser.add_argument("--input-dir", type=str, default="eval/data/inputs/proposals",
                       help="Directory containing input proposals")
    parser.add_argument("--output-dir", type=str, default="eval/data",
                       help="Base directory for outputs")
    parser.add_argument("--model", type=str, default="gpt4",
                       help="Model to use (gpt4)")
    parser.add_argument("--api-key", type=str, required=True,
                       help="API key for the model")
    parser.add_argument("--name", type=str, required=True,
                       help="Experiment name")
    args = parser.parse_args()
    
    # Load proposals
    proposals = await load_proposals(args.input_dir)
    print(f"Loaded {len(proposals)} proposals")
    
    # Initialize model
    if args.model == "gpt4":
        model = GPT4Model(api_key=args.api_key)
    else:
        raise ValueError(f"Unknown model: {args.model}")
    
    # Run experiment
    evaluator = Evaluator(model, output_dir=args.output_dir)
    exp_id = await evaluator.run_experiment(
        name=args.name,
        proposals=proposals
    )
    
    print(f"Experiment completed: {exp_id}")
    print(f"Results saved in: {args.output_dir}/experiments/{exp_id}")

if __name__ == "__main__":
    asyncio.run(main()) 