# Zoning Proposal Evaluation

Evaluation framework for analyzing LLM-generated community feedback on zoning proposals.

## Structure

```
eval/
├── data/                    # Data storage
│   ├── inputs/             # Input proposals
│   ├── ground_truth/       # Ground truth data
│   └── experiments/        # Experiment results
├── src/                    # Source code
│   ├── models/            # Model implementations
│   ├── schemas.py         # Data structures
│   └── evaluator.py       # Evaluation logic
└── scripts/               # Utility scripts
```

## Model Specification

Models should implement the `BaseModel` interface:

```python
async def __call__(self, proposal: ZoningProposal) -> EvaluationResult:
    """
    Generate community feedback for a zoning proposal
    Args:
        proposal: Input proposal with zoning details
    Returns:
        EvaluationResult: Generated feedback including:
            - Opinion distribution (support/neutral/oppose)
            - Representative comments from different demographics
            - Key themes in support and opposition
    """
```

### Input Format (ZoningProposal)
```json
{
    "grid_config": {
        "cellSize": 100,
        "bounds": {
            "north": 37.8120,
            "south": 37.7080,
            "east": -122.3549,
            "west": -122.5157
        }
    },
    "height_limits": {
        "default": 40,
        "options": [40, 65, 80, 85, 105]
    },
    "cells": {
        "cell_id": {
            "height_limit": 65,
            "category": "residential",
            "last_updated": "2024-03-15",
            "bbox": {
                "north": 37.7371,
                "south": 37.7261,
                "east": -122.4887,
                "west": -122.4997
            }
        }
    }
}
```

### Output Format (EvaluationResult)
```json
{
    "summary": {
        "support": 65,
        "neutral": 15,
        "oppose": 20
    },
    "comments": [
        {
            "id": 1,
            "agent": {
                "age": "26-40",
                "income_level": "middle_income",
                "education_level": "bachelor",
                "occupation": "white_collar",
                "gender": "female"
            },
            "opinion": "support",
            "comment": "...",
            "cell_id": "cell_id"
        }
    ],
    "key_themes": {
        "support": ["housing needs", "urban development"],
        "oppose": ["traffic concerns", "shadow impact"]
    }
}
```

## Usage

```python
from eval.src.models.gpt4 import GPT4Model
from eval.src.evaluator import Evaluator

# Initialize model and evaluator
model = GPT4Model(api_key="your-api-key")
evaluator = Evaluator(model)

# Run evaluation
exp_id = await evaluator.run_experiment(
    name="height_limit_study",
    proposals=proposals
)
```

## Evaluation Metrics

1. Opinion Distribution Difference
   - Measures similarity between predicted and ground truth opinion distributions
   - Range: 0 (identical) to 1 (completely different)

2. Theme Overlap
   - Measures overlap between predicted and ground truth key themes
   - Calculated separately for supporting and opposing themes
   - Range: 0 (no overlap) to 1 (perfect overlap)

## Adding New Models

1. Create new model class in `src/models/`
2. Inherit from `BaseModel`
3. Implement `__call__` method

Example:
```python
class NewModel(BaseModel):
    async def __call__(self, proposal: ZoningProposal) -> EvaluationResult:
        # Implement feedback generation logic
        pass
``` 