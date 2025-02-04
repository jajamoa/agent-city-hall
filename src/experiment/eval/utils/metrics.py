"""Metrics calculation utilities for experiment evaluation."""
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
from .data_models import EvaluationResult

class MetricsCalculator:
    """Generic metrics calculator"""
    
    @staticmethod
    def calculate_distribution(
        result: EvaluationResult,
        group_by_field: str,
        target_field: str = "opinion",
        value_extractor: Optional[Callable[[Any], str]] = None
    ) -> Dict[str, Dict[str, float]]:
        """Calculate distribution of any field
        
        Args:
            result: Evaluation result
            group_by_field: Field path for grouping (e.g., "agent.age", "agent.income_level")
            target_field: Target field path for distribution (e.g., "opinion", "agent.gender")
            value_extractor: Optional function to customize value extraction
            
        Returns:
            Dict[str, Dict[str, float]]: Distribution of target field in each group
            Example: {
                "group1": {"value1": 0.3, "value2": 0.7},
                "group2": {"value1": 0.5, "value2": 0.5}
            }
        """
        groups = defaultdict(lambda: defaultdict(int))
        group_totals = defaultdict(int)
        
        def get_field_value(obj: Any, field_path: str) -> Any:
            """Get object attribute value through field path"""
            for part in field_path.split('.'):
                obj = getattr(obj, part)
            return obj
        
        # Count values in each group
        for item in result.comments:
            group = str(get_field_value(item, group_by_field))
            if value_extractor:
                value = value_extractor(get_field_value(item, target_field))
            else:
                value = str(get_field_value(item, target_field))
            
            groups[group][value] += 1
            group_totals[group] += 1
        
        # Convert to percentages
        distribution = {}
        for group, counts in groups.items():
            total = group_totals[group]
            distribution[group] = {
                value: count / total
                for value, count in counts.items()
            }
        
        return distribution
    
    @staticmethod
    def calculate_similarity(
        result: EvaluationResult,
        ground_truth: EvaluationResult,
        compare_fields: List[str],
        value_extractors: Optional[Dict[str, Callable[[Any], Any]]] = None
    ) -> Dict[str, float]:
        """Calculate similarity between two results for specified fields
        
        Args:
            result: Model output result
            ground_truth: Ground truth result
            compare_fields: List of field paths to compare
            value_extractors: Optional mapping of field to value extraction functions
            
        Returns:
            Dict[str, float]: Similarity scores (0-1) for each field
        """
        def get_distribution(comments: List[Any], field: str) -> Dict[str, float]:
            counts = defaultdict(int)
            total = len(comments)
            
            for comment in comments:
                parts = field.split('.')
                value = comment
                for part in parts:
                    value = getattr(value, part)
                
                if value_extractors and field in value_extractors:
                    value = value_extractors[field](value)
                else:
                    value = str(value)
                    
                counts[value] += 1
                
            return {k: v/total for k, v in counts.items()}
        
        similarity = {}
        for field in compare_fields:
            result_dist = get_distribution(result.comments, field)
            truth_dist = get_distribution(ground_truth.comments, field)
            
            # Calculate distribution similarity (1 - average absolute difference)
            all_values = set(result_dist.keys()) | set(truth_dist.keys())
            total_diff = sum(
                abs(result_dist.get(val, 0) - truth_dist.get(val, 0))
                for val in all_values
            )
            similarity[field] = 1 - (total_diff / 2)
        
        return similarity

def calculate_metrics(
    result: EvaluationResult,
    ground_truth: Optional[EvaluationResult] = None,
    distribution_configs: Optional[List[Dict[str, Any]]] = None,
    similarity_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Calculate all configured metrics
    
    Args:
        result: Result to evaluate
        ground_truth: Optional ground truth result
        distribution_configs: List of distribution calculation configs, each containing:
            - group_by_field: Field to group by
            - target_field: Target field (optional, defaults to "opinion")
            - value_extractor: Value extraction function (optional)
        similarity_fields: List of fields to calculate similarity for
        
    Returns:
        Dict[str, Any]: All calculated metrics
    """
    calculator = MetricsCalculator()
    metrics = {"distributions": {}}
    
    # Calculate distribution metrics
    if distribution_configs:
        for config in distribution_configs:
            group_by = config["group_by_field"]
            target = config.get("target_field", "opinion")
            extractor = config.get("value_extractor")
            
            metrics["distributions"][group_by] = calculator.calculate_distribution(
                result,
                group_by_field=group_by,
                target_field=target,
                value_extractor=extractor
            )
    
    # Calculate similarity metrics if ground truth exists
    if ground_truth and similarity_fields:
        metrics["similarities"] = calculator.calculate_similarity(
            result,
            ground_truth,
            compare_fields=similarity_fields
        )
    
    return metrics 