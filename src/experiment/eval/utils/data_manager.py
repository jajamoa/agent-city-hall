"""Data management utilities for experiments."""
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Union
import json
from datetime import datetime
import sys
import os
from .data_models import ZoningProposal, EvaluationResult
from .metrics import calculate_metrics

class DataManager:
    """Manages experiment data storage and retrieval."""
    
    def __init__(self, base_dir: str = "src/experiment"):
        """Initialize data manager with directory structure."""
        self.base_dir = Path(base_dir)
        self.eval_dir = self.base_dir / "eval"
        self.inputs_dir = self.eval_dir / "data/inputs"
        self.ground_truth_dir = self.eval_dir / "data/ground_truth"
        self.log_dir = self.base_dir / "log"
        self._init_directories()
    
    def _init_directories(self):
        """Create necessary directory structure if not exists."""
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.ground_truth_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def create_experiment(self, name: str, model_name: str) -> Tuple[Path, str]:
        """Create experiment directory with unique ID.
        
        Returns:
            Tuple[Path, str]: (experiment directory path, experiment ID)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_id = f"{name}_{model_name}_{timestamp}"
        exp_dir = self.log_dir / exp_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        return exp_dir, exp_id
    
    def save_metadata(self, 
                     exp_dir: Path,
                     args: Union[Dict[str, Any], Any],
                     start_time: datetime,
                     end_time: datetime) -> None:
        """Save experiment metadata including runtime information and parameters."""
        if isinstance(args, dict):
            metadata = args
        else:
            # Handle legacy argparse.Namespace format
            metadata = {
                "parameters": {
                    "model": args.model,
                    "population": args.population,
                    "name": args.name
                },
                "runtime": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds()
                },
                "environment": {
                    "python_version": sys.version,
                    "command": " ".join(sys.argv),
                    "working_directory": os.getcwd()
                }
            }
        
        with open(exp_dir / "experiment_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def load_ground_truth(self, proposal_id: str) -> Optional[EvaluationResult]:
        """Load ground truth data for a proposal if exists."""
        gt_path = self.ground_truth_dir / f"{proposal_id}_gt.json"
        if not gt_path.exists():
            return None
        
        with open(gt_path) as f:
            data = json.load(f)
            return EvaluationResult.model_validate(data)
    
    def save_experiment_result(self, 
                             exp_dir: Path,
                             proposal: ZoningProposal,
                             result: Dict[str, Any],
                             proposal_id: str,
                             model_name: str,
                             metrics: Optional[Dict[str, Any]] = None):
        """Save experiment input, output and metrics."""
        # Extract number from proposal_id (e.g., "proposal_000" -> "000")
        file_id = proposal_id.split("_")[-1]
        
        # Save input proposal
        input_path = exp_dir / f"{file_id}_input.json"
        with open(input_path, "w") as f:
            json.dump(proposal.model_dump(), f, indent=2)
        
        # Save output result
        output_path = exp_dir / f"{file_id}_output.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        
        # Save metrics if provided
        if metrics:
            metrics_path = exp_dir / f"{file_id}_metrics.json"
            with open(metrics_path, "w") as f:
                json.dump(metrics, f, indent=2) 