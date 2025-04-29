"""
Survey opinion evaluator module.

This module provides evaluation metrics for comparing agent opinion predictions 
with ground truth from survey data. It supports evaluating both opinion scores 
and reason selections.
"""
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Type, Set
import numpy as np

class Evaluator:
    """Base evaluator interface"""
    
    def __init__(self, name: str):
        self.name = name
    
    def evaluate(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate predictions against ground truth"""
        raise NotImplementedError()

class OpinionScoreEvaluator(Evaluator):
    """Evaluates opinion score accuracy"""
    
    def __init__(self):
        super().__init__("opinion_score")
    
    def evaluate(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate opinion score accuracy"""
        results = {
            "mean_absolute_error": 0.0,
            "region_errors": {},
            "correlation": 0.0
        }
        
        all_gt_scores = []
        all_pred_scores = []
        errors = []
        region_errors = {}
        
        for user_id, gt_user in ground_truth.items():
            if user_id in predicted:
                pred_user = predicted[user_id]
                
                for region_id, gt_score in gt_user.get("opinions", {}).items():
                    pred_score = pred_user.get("opinions", {}).get(region_id)
                    
                    if pred_score is not None:
                        all_gt_scores.append(gt_score)
                        all_pred_scores.append(pred_score)
                        
                        error = abs(gt_score - pred_score)
                        errors.append(error)
                        
                        if region_id not in region_errors:
                            region_errors[region_id] = []
                        region_errors[region_id].append(error)
        
        if errors:
            results["mean_absolute_error"] = sum(errors) / len(errors)
        
        for region_id, error_list in region_errors.items():
            if error_list:
                results["region_errors"][region_id] = sum(error_list) / len(error_list)
        
        if len(all_gt_scores) > 1:
            try:
                correlation = np.corrcoef(all_gt_scores, all_pred_scores)[0, 1]
                results["correlation"] = float(correlation)
            except:
                results["correlation"] = float('nan')
        
        return results

class ReasonMatchEvaluator(Evaluator):
    """Evaluates reason selection accuracy using Jaccard similarity"""
    
    def __init__(self):
        super().__init__("reason_match")
    
    def evaluate(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate reason selection accuracy"""
        results = {
            "jaccard_similarity": 0.0,
            "region_similarities": {},
            "most_common_correct": {},
            "most_common_incorrect": {}
        }
        
        similarities = []
        region_similarities = {}
        correct_reasons = {}
        incorrect_reasons = {}
        
        for user_id, gt_user in ground_truth.items():
            if user_id in predicted:
                pred_user = predicted[user_id]
                
                for region_id, gt_reasons in gt_user.get("reasons", {}).items():
                    pred_reasons = pred_user.get("reasons", {}).get(region_id)
                    
                    if pred_reasons is not None:
                        gt_set = set(gt_reasons)
                        pred_set = set(pred_reasons)
                        
                        intersection = len(gt_set.intersection(pred_set))
                        union = len(gt_set.union(pred_set))
                        
                        similarity = intersection / union if union > 0 else 1.0
                        similarities.append(similarity)
                        
                        if region_id not in region_similarities:
                            region_similarities[region_id] = []
                        region_similarities[region_id].append(similarity)
                        
                        for reason in pred_set.intersection(gt_set):
                            if region_id not in correct_reasons:
                                correct_reasons[region_id] = {}
                            if reason not in correct_reasons[region_id]:
                                correct_reasons[region_id][reason] = 0
                            correct_reasons[region_id][reason] += 1
                        
                        for reason in pred_set.difference(gt_set):
                            if region_id not in incorrect_reasons:
                                incorrect_reasons[region_id] = {}
                            if reason not in incorrect_reasons[region_id]:
                                incorrect_reasons[region_id][reason] = 0
                            incorrect_reasons[region_id][reason] += 1
        
        if similarities:
            results["jaccard_similarity"] = sum(similarities) / len(similarities)
        
        for region_id, sim_list in region_similarities.items():
            if sim_list:
                results["region_similarities"][region_id] = sum(sim_list) / len(sim_list)
        
        for region_id, reasons in correct_reasons.items():
            sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)
            results["most_common_correct"][region_id] = sorted_reasons[:3] if sorted_reasons else []
        
        for region_id, reasons in incorrect_reasons.items():
            sorted_reasons = sorted(reasons.items(), key=lambda x: x[1], reverse=True)
            results["most_common_incorrect"][region_id] = sorted_reasons[:3] if sorted_reasons else []
        
        return results

# Registry of available evaluators
EVALUATOR_REGISTRY = {
    "opinion_score": OpinionScoreEvaluator,
    "reason_match": ReasonMatchEvaluator
}

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load JSON file and return its contents"""
    with open(file_path, 'r') as f:
        return json.load(f)

def transform_output_to_survey_format(output_data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform model output format to match survey format"""
    transformed = {}
    
    # Map opinion string to numeric scale
    opinion_mapping = {
        "oppose": 3,
        "neutral": 5,
        "support": 8
    }
    
    for comment in output_data.get("comments", []):
        user_id = comment.get("id", "")
        opinion_value = comment.get("opinion", "neutral")
        cell_id = comment.get("cell_id", "1.1")
        
        score = opinion_mapping.get(opinion_value, 5)
        
        if user_id not in transformed:
            transformed[user_id] = {
                "opinions": {},
                "reasons": {}
            }
        
        transformed[user_id]["opinions"][cell_id] = score
        
        if "reasons" in comment:
            transformed[user_id]["reasons"][cell_id] = comment["reasons"]
    
    return transformed

def evaluate_files(output_file: Path, ground_truth_file: Path, evaluator_names: List[str]) -> Dict[str, Any]:
    """Evaluate output against ground truth using specified evaluators"""
    results = {}
    
    try:
        # Load data
        output_data = load_json_file(output_file)
        ground_truth_data = load_json_file(ground_truth_file)
        
        # Transform output if needed
        if "comments" in output_data:
            predicted_data = transform_output_to_survey_format(output_data)
        else:
            predicted_data = output_data
        
        # Run evaluators
        for name in evaluator_names:
            if name in EVALUATOR_REGISTRY:
                evaluator = EVALUATOR_REGISTRY[name]()
                results[evaluator.name] = evaluator.evaluate(predicted_data, ground_truth_data)
            else:
                print(f"Warning: Unknown evaluator '{name}'")
        
    except Exception as e:
        print(f"Error evaluating: {str(e)}")
        results["error"] = str(e)
    
    return results

def run_evaluators(
    output_files: List[Path], 
    ground_truth_files: List[Path], 
    evaluator_names: List[str]
) -> Dict[str, Any]:
    """Run specified evaluators on multiple file pairs"""
    results = {}
    
    if not evaluator_names:
        print("No evaluators specified")
        return results
    
    # Match output files with ground truth files
    for output_file in output_files:
        proposal_id = output_file.name.split('_output.json')[0]
        gt_file = next((f for f in ground_truth_files if f.name.startswith(proposal_id)), None)
        
        if gt_file:
            # Run evaluation
            eval_results = evaluate_files(output_file, gt_file, evaluator_names)
            results[proposal_id] = eval_results
        else:
            print(f"No matching ground truth for {output_file}")
    
    return results

def evaluate_experiment_dir(experiment_dir: Path, evaluator_names: List[str]) -> Dict[str, Any]:
    """Evaluate all output files in an experiment directory"""
    results = {}
    
    # Find output and ground truth files
    output_files = list(experiment_dir.glob("*_output.json"))
    ground_truth_files = list(experiment_dir.glob("*_ground_truth.json"))
    
    if not output_files:
        print("No output files found in experiment directory.")
        return results
    
    if not ground_truth_files:
        print("No ground truth files found in experiment directory.")
        return results
    
    # Match output files with ground truth files
    for output_file in output_files:
        proposal_id = output_file.stem.rsplit("_output", 1)[0]
        gt_file = next((f for f in ground_truth_files if f.stem.startswith(proposal_id)), None)
        
        if gt_file:
            print(f"Evaluating {proposal_id}...")
            # Run evaluation
            proposal_results = evaluate_files(output_file, gt_file, evaluator_names)
            results[proposal_id] = proposal_results
            
            # Print summary
            for evaluator_name, metrics in proposal_results.items():
                if evaluator_name == "opinion_score":
                    print(f"  Opinion Score MAE: {metrics.get('mean_absolute_error', 'N/A'):.4f}")
                    print(f"  Opinion Correlation: {metrics.get('correlation', 'N/A'):.4f}")
                elif evaluator_name == "reason_match":
                    print(f"  Reason Match Similarity: {metrics.get('jaccard_similarity', 'N/A'):.4f}")
        else:
            print(f"No matching ground truth file for {output_file.name}")
    
    return results

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="Evaluate model outputs against ground truth")
    
    # Input options - either file pair or experiment directory
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", "-o", help="Path to output JSON file")
    group.add_argument("--experiment-dir", "-d", help="Path to experiment directory")
    
    # Ground truth required only for file evaluation
    parser.add_argument("--ground-truth", "-g", help="Path to ground truth JSON file (required with --output)")
    
    # Other options
    parser.add_argument("--evaluators", "-e", nargs="+", default=list(EVALUATOR_REGISTRY.keys()),
                      help=f"Evaluators to run (available: {', '.join(EVALUATOR_REGISTRY.keys())})")
    parser.add_argument("--save", "-s", help="Path to save results JSON")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.output and not args.ground_truth:
        parser.error("--ground-truth is required when using --output")
    
    # Run evaluation based on input type
    if args.experiment_dir:
        # Evaluate experiment directory
        experiment_dir = Path(args.experiment_dir)
        if not experiment_dir.exists() or not experiment_dir.is_dir():
            print(f"Error: Experiment directory not found: {args.experiment_dir}")
            return 1
        
        results = evaluate_experiment_dir(experiment_dir, args.evaluators)
        
        # Determine save path
        save_path = Path(args.save) if args.save else experiment_dir / "evaluation_results.json"
        
    else:
        # Evaluate single file pair
        output_file = Path(args.output)
        ground_truth_file = Path(args.ground_truth)
        
        if not output_file.exists():
            print(f"Error: Output file not found: {args.output}")
            return 1
        
        if not ground_truth_file.exists():
            print(f"Error: Ground truth file not found: {args.ground_truth}")
            return 1
        
        results = evaluate_files(output_file, ground_truth_file, args.evaluators)
        
        # Print summary for single file evaluation
        print("\nEvaluation Summary:")
        for evaluator_name, metrics in results.items():
            if evaluator_name == "opinion_score":
                print(f"Opinion Score MAE: {metrics.get('mean_absolute_error', 'N/A'):.4f}")
                print(f"Opinion Correlation: {metrics.get('correlation', 'N/A'):.4f}")
            elif evaluator_name == "reason_match":
                print(f"Reason Match Similarity: {metrics.get('jaccard_similarity', 'N/A'):.4f}")
        
        # Determine save path
        save_path = Path(args.save) if args.save else None
    
    # Save results if path is specified
    if save_path:
        with open(save_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {save_path}")
    elif not args.experiment_dir:
        # Print detailed results for single file if not saving
        print("\nDetailed Results:")
        print(json.dumps(results, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 