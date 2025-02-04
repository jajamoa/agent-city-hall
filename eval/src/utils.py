from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
from .schemas import ZoningProposal, EvaluationResult, ExperimentResult

class DataManager:
    """Unified data management for evaluation experiments"""
    
    def __init__(self, base_dir: str = "eval/data"):
        """
        Initialize DataManager with directory structure
        Args:
            base_dir: Root directory for all evaluation data
        """
        self.base_dir = Path(base_dir)
        self.inputs_dir = self.base_dir / "inputs" / "proposals"
        self.ground_truth_dir = self.base_dir / "ground_truth"
        self.experiments_dir = self.base_dir / "experiments"
        self._init_directories()
    
    def _init_directories(self):
        """Create necessary directory structure if not exists"""
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.ground_truth_dir.mkdir(parents=True, exist_ok=True)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
    
    def save_proposal(self, proposal: ZoningProposal, name: str):
        """
        Save a zoning proposal to the inputs directory
        Args:
            proposal: The proposal to save
            name: Identifier for the proposal
        """
        file_path = self.inputs_dir / f"{name}.json"
        with open(file_path, "w") as f:
            json.dump(proposal.model_dump(), f, indent=2)
    
    def save_ground_truth(self, result: EvaluationResult, proposal_id: str):
        """
        Save ground truth evaluation result
        Args:
            result: The ground truth evaluation result
            proposal_id: ID of the corresponding proposal
        """
        file_path = self.ground_truth_dir / f"{proposal_id}_gt.json"
        with open(file_path, "w") as f:
            json.dump(result.model_dump(), f, indent=2)
    
    def create_experiment(self, name: str) -> str:
        """
        Create a new experiment directory
        Args:
            name: Name of the experiment
        Returns:
            str: Generated experiment ID
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_id = f"exp_{timestamp}_{name}"
        exp_dir = self.experiments_dir / exp_id
        (exp_dir / "results").mkdir(parents=True, exist_ok=True)
        (exp_dir / "viz").mkdir(parents=True, exist_ok=True)
        return exp_id
    
    def save_experiment_result(self, 
                             exp_id: str,
                             result: EvaluationResult,
                             proposal_id: str,
                             model_name: str,
                             metadata: Optional[Dict[str, Any]] = None):
        """
        Save an experiment result
        Args:
            exp_id: Experiment identifier
            result: Evaluation result
            proposal_id: ID of the evaluated proposal
            model_name: Name of the model used
            metadata: Additional experiment metadata
        """
        exp_result = ExperimentResult(
            timestamp=datetime.now(),
            model_name=model_name,
            proposal_id=proposal_id,
            result=result,
            metadata=metadata
        )
        
        file_path = self.experiments_dir / exp_id / "results" / f"{proposal_id}.json"
        with open(file_path, "w") as f:
            json.dump(exp_result.model_dump(), f, indent=2)
    
    def generate_experiment_report(self, exp_id: str):
        """
        Generate visualization report for experiment results
        Args:
            exp_id: Experiment identifier
        """
        exp_dir = self.experiments_dir / exp_id
        results_dir = exp_dir / "results"
        viz_dir = exp_dir / "viz"
        
        # Load all results
        results = []
        for file_path in results_dir.glob("*.json"):
            with open(file_path) as f:
                results.append(ExperimentResult.model_validate(json.load(f)))
        
        if not results:
            return
        
        # Prepare DataFrame for visualization
        df_data = []
        for r in results:
            summary = r.result.summary
            total = sum(summary.values())
            df_data.append({
                "proposal_id": r.proposal_id,
                "model": r.model_name,
                "timestamp": r.timestamp,
                "support_rate": summary["support"] / total,
                "oppose_rate": summary["oppose"] / total,
                "neutral_rate": summary["neutral"] / total
            })
        
        df = pd.DataFrame(df_data)
        
        # Generate visualization plots
        fig = px.line(df, x="timestamp", y="support_rate", 
                     color="model", title="Support Rate Trend")
        fig.write_html(str(viz_dir / "support_trend.html"))
        
        fig = px.bar(df, x="proposal_id",
                    y=["support_rate", "neutral_rate", "oppose_rate"],
                    title="Opinion Distribution")
        fig.write_html(str(viz_dir / "opinion_dist.html")) 