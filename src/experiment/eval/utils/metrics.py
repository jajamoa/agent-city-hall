"""Metrics calculation utilities for experiment evaluation."""
from typing import Dict, List, Any, Optional
from collections import defaultdict
import numpy as np
from scipy.stats import entropy
from scipy.spatial.distance import jensenshannon

def calculate_distribution_distance(p: Dict[str, float], q: Dict[str, float]) -> Dict[str, float]:
    """Calculate various distance metrics between two discrete distributions
    
    Args:
        p: First distribution
        q: Second distribution
        
    Returns:
        Dict containing different distance metrics
    """
    # Ensure both distributions have the same keys
    all_keys = sorted(set(p.keys()) | set(q.keys()))
    p_vec = np.array([p.get(k, 0.0) for k in all_keys])
    q_vec = np.array([q.get(k, 0.0) for k in all_keys])
    
    # Normalize if not already normalized
    p_vec = p_vec / p_vec.sum() if p_vec.sum() > 0 else p_vec
    q_vec = q_vec / q_vec.sum() if q_vec.sum() > 0 else q_vec
    
    # Calculate metrics
    metrics = {}
    
    # Jensen-Shannon Divergence (symmetric, bounded between 0 and 1)
    metrics["js_divergence"] = float(jensenshannon(p_vec, q_vec))
    
    # Chi-square Distance
    chi_square = np.sum(np.square(p_vec - q_vec) / (p_vec + q_vec + 1e-10)) / 2
    metrics["chi_square"] = float(chi_square)
    
    # Total Variation Distance (L1 distance / 2)
    metrics["total_variation"] = float(np.sum(np.abs(p_vec - q_vec)) / 2)
    
    return metrics

def calculate_metrics(
    result: Dict[str, Any],
    ground_truth: Dict[str, Any],
    metric_type: str,
    group_field: Optional[str] = None,
    group_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Calculate metrics based on type
    
    Args:
        result: Model output
        ground_truth: Ground truth data
        metric_type: Type of metric to calculate
        group_field: Field to group by (for distribution metrics)
        group_metadata: Group definitions (for distribution metrics)
        
    Returns:
        Dict containing calculated metrics
    """
    if metric_type == "group_distribution":
        return calculate_distribution_metrics(result, ground_truth, group_field, group_metadata)
    elif metric_type == "individual_match":
        return calculate_individual_metrics(result, ground_truth)
    else:
        raise ValueError(f"Unknown metric type: {metric_type}")

def parse_age_range(age: int) -> int:
    """Parse age value
    
    Args:
        age: Integer age value
        
    Returns:
        int: The same age value
    """
    return age

def calculate_distribution_metrics(
    result: Dict[str, Any],
    ground_truth: Dict[str, Any],
    group_field: str,
    group_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate distribution metrics
    
    Args:
        result: Model output with comments
        ground_truth: Ground truth distributions
        group_field: Field to group by (e.g., "agent.age")
        group_metadata: Group definitions with ranges
        
    Returns:
        Dict containing:
        - predicted_distribution: Calculated distribution from model output
        - metrics: Statistical metrics
    """
    # Calculate distribution of predicted results based on group rules
    predicted_dist = defaultdict(lambda: defaultdict(int))
    group_totals = defaultdict(int)
    total_counts = defaultdict(int)
    total = 0
    
    # Initialize predicted distribution with all groups and opinions
    predicted_distribution = {}
    for group_name in group_metadata.keys():
        predicted_distribution[group_name] = {
            "support": 0.0,
            "neutral": 0.0,
            "oppose": 0.0
        }
    
    for comment in result["comments"]:
        # Get agent attribute value
        parts = group_field.split('.')
        value = comment
        for part in parts:
            value = value[part] if isinstance(value, dict) else getattr(value, part)
            
        # Determine group based on metadata rules
        group = None
        for group_name, rules in group_metadata.items():
            try:
                if group_field == "agent.age":
                    # Special handling for age ranges
                    age_value = value  # value is already an integer
                    if rules["min"] <= age_value <= rules["max"]:
                        group = group_name
                        break
                else:
                    # Direct match for other fields
                    if value == group_name:
                        group = group_name
                        break
            except (ValueError, AttributeError) as e:
                print(f"Warning: Failed to parse value '{value}' for group '{group_name}': {e}")
                continue
        
        if group:
            opinion = comment["opinion"]
            predicted_dist[group][opinion] += 1
            group_totals[group] += 1
            total_counts[opinion] += 1
            total += 1
        else:
            print(f"Warning: Could not assign value '{value}' to any group in {list(group_metadata.keys())}")
    
    # Convert to percentages for each group
    for group, counts in predicted_dist.items():
        group_total = group_totals[group]
        if group_total > 0:  # Avoid division by zero
            for opinion in ["support", "neutral", "oppose"]:
                predicted_distribution[group][opinion] = counts.get(opinion, 0) / group_total
    
    # Add overall statistics
    if total > 0:
        predicted_distribution["overall"] = {
            "support": total_counts.get("support", 0) / total,
            "neutral": total_counts.get("neutral", 0) / total,
            "oppose": total_counts.get("oppose", 0) / total
        }
    else:
        predicted_distribution["overall"] = {
            "support": 0.0,
            "neutral": 0.0,
            "oppose": 0.0
        }
    
    # Calculate distribution metrics for each group
    metrics = defaultdict(dict)
    for group in ground_truth.keys():
        if group != "overall":  # Skip overall statistics for metrics calculation
            pred_dist = predicted_distribution.get(group, {})
            true_dist = ground_truth[group]
            group_metrics = calculate_distribution_distance(pred_dist, true_dist)
            metrics[group] = group_metrics
    
    # Calculate average metrics across groups
    avg_metrics = {}
    if metrics:
        for metric_name in ["js_divergence", "chi_square", "total_variation"]:
            avg_metrics[f"avg_{metric_name}"] = float(np.mean([
                m[metric_name] for m in metrics.values()
            ]))
    
    return {
        "predicted_distribution": predicted_distribution,
        "group_metrics": dict(metrics),  # Convert defaultdict to dict
        "average_metrics": avg_metrics
    }

def calculate_individual_metrics(
    result: Dict[str, Any],
    ground_truth: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate individual matching metrics
    
    Args:
        result: Model output with comments
        ground_truth: Ground truth individual responses
        
    Returns:
        Dict containing matching metrics
    """
    total_matches = 0
    opinion_matches = 0
    matched_pairs = []
    
    # Create mapping from ID to comments
    result_dict = {str(c["id"]): c for c in result["comments"]}
    
    # Compare each individual
    total_individuals = len(ground_truth)
    for person_id, gt_data in ground_truth.items():
        if person_id in result_dict:
            result_comment = result_dict[person_id]
            
            # Record matches
            if result_comment["opinion"] == gt_data["opinion"]:
                opinion_matches += 1
                total_matches += 1
            
            # Store matched pairs
            matched_pairs.append({
                "id": person_id,
                "predicted_opinion": result_comment["opinion"],
                "true_opinion": gt_data["opinion"]
            })
    
    return {
        "metrics": {
            "total_accuracy": total_matches / total_individuals,
            "opinion_accuracy": opinion_matches / total_individuals,
            "matched_count": len(matched_pairs)
        },
        "matched_pairs": matched_pairs
    } 