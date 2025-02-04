from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
from .schemas import ZoningProposal, EvaluationResult
from .models.base import BaseModel

class Evaluator:
    """Evaluator for comparing model outputs with ground truth"""
    
    def __init__(self, model: BaseModel, output_dir: str = "eval/data"):
        """
        Initialize evaluator
        Args:
            model: Model implementation to use
            output_dir: Directory for storing results
        """
        self.model = model
        self.output_dir = Path(output_dir)
        self._init_directories()
    
    def _init_directories(self):
        """Create necessary directories"""
        (self.output_dir / "inputs").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "ground_truth").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "experiments").mkdir(parents=True, exist_ok=True)
    
    def load_ground_truth(self, proposal_id: str) -> Optional[EvaluationResult]:
        """
        Load ground truth for a proposal
        Args:
            proposal_id: Proposal identifier
        Returns:
            EvaluationResult: Ground truth if exists
        """
        gt_path = self.output_dir / "ground_truth" / f"{proposal_id}_gt.json"
        if not gt_path.exists():
            return None
        with open(gt_path) as f:
            return EvaluationResult.model_validate(json.load(f))
    
    async def evaluate_single(self, 
                            proposal: ZoningProposal,
                            proposal_id: str) -> Dict[str, Any]:
        """
        Evaluate single proposal and compare with ground truth
        Args:
            proposal: Input proposal
            proposal_id: Proposal identifier
        Returns:
            Dict: Evaluation metrics
        """
        # Get model output
        model_output = await self.model(proposal)
        
        # Load ground truth
        ground_truth = self.load_ground_truth(proposal_id)
        if ground_truth is None:
            return {
                "model_output": model_output,
                "metrics": None
            }
        
        # Compare with ground truth
        metrics = self._compute_metrics(model_output, ground_truth)
        
        return {
            "model_output": model_output,
            "ground_truth": ground_truth,
            "metrics": metrics
        }
    
    def _compute_metrics(self,
                        output: EvaluationResult,
                        ground_truth: EvaluationResult) -> Dict[str, float]:
        """
        Compute comparison metrics
        Args:
            output: Model output
            ground_truth: Ground truth
        Returns:
            Dict: Metrics
        """
        # Calculate opinion distribution similarity
        out_total = sum(output.summary.values())
        gt_total = sum(ground_truth.summary.values())
        
        opinion_diff = sum(
            abs(output.summary[k]/out_total - ground_truth.summary[k]/gt_total)
            for k in output.summary
        ) / len(output.summary)
        
        # Calculate theme overlap
        support_overlap = len(
            set(output.key_themes["support"]) & 
            set(ground_truth.key_themes["support"])
        ) / len(ground_truth.key_themes["support"])
        
        oppose_overlap = len(
            set(output.key_themes["oppose"]) & 
            set(ground_truth.key_themes["oppose"])
        ) / len(ground_truth.key_themes["oppose"])
        
        return {
            "opinion_distribution_difference": opinion_diff,
            "support_theme_overlap": support_overlap,
            "oppose_theme_overlap": oppose_overlap
        }
    
    async def run_experiment(self, 
                           name: str,
                           proposals: List[ZoningProposal]) -> str:
        """
        Run evaluation experiment
        Args:
            name: Experiment name
            proposals: List of proposals to evaluate
        Returns:
            str: Experiment directory path
        """
        # Create experiment directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exp_id = f"exp_{timestamp}_{name}"
        exp_dir = self.output_dir / "experiments" / exp_id
        results_dir = exp_dir / "results"
        viz_dir = exp_dir / "viz"
        results_dir.mkdir(parents=True)
        viz_dir.mkdir(parents=True)
        
        # Evaluate each proposal
        all_results = []
        for i, proposal in enumerate(proposals):
            proposal_id = f"proposal_{i:03d}"
            
            # Save input
            proposal_path = results_dir / f"{proposal_id}.json"
            with open(proposal_path, "w") as f:
                json.dump(proposal.model_dump(), f, indent=2)
            
            # Run evaluation
            result = await self.evaluate_single(proposal, proposal_id)
            all_results.append(result)
            
            # Save result
            result_path = results_dir / f"{proposal_id}_result.json"
            with open(result_path, "w") as f:
                json.dump({
                    "model_output": result["model_output"].model_dump(),
                    "metrics": result["metrics"]
                }, f, indent=2)
        
        # Generate report
        self._generate_report(all_results, viz_dir)
        return exp_id
    
    def _generate_report(self, results: List[Dict], viz_dir: Path):
        """Generate visualization report"""
        # Prepare metrics data
        df_metrics = []
        for i, r in enumerate(results):
            if r["metrics"] is not None:
                df_metrics.append({
                    "proposal_id": f"proposal_{i:03d}",
                    **r["metrics"]
                })
        
        if df_metrics:
            df = pd.DataFrame(df_metrics)
            
            # Plot metrics
            fig = px.line(df, x="proposal_id", y="opinion_distribution_difference",
                         title="Opinion Distribution Difference")
            fig.write_html(str(viz_dir / "opinion_diff.html"))
            
            fig = px.line(df, x="proposal_id", 
                         y=["support_theme_overlap", "oppose_theme_overlap"],
                         title="Theme Overlap")
            fig.write_html(str(viz_dir / "theme_overlap.html"))
        
        # Plot model outputs
        df_outputs = []
        for i, r in enumerate(results):
            output = r["model_output"]
            total = sum(output.summary.values())
            df_outputs.append({
                "proposal_id": f"proposal_{i:03d}",
                "support_rate": output.summary["support"] / total,
                "oppose_rate": output.summary["oppose"] / total,
                "neutral_rate": output.summary["neutral"] / total
            })
        
        df = pd.DataFrame(df_outputs)
        fig = px.bar(df, x="proposal_id",
                    y=["support_rate", "neutral_rate", "oppose_rate"],
                    title="Model Output Distribution")
        fig.write_html(str(viz_dir / "model_output.html")) 