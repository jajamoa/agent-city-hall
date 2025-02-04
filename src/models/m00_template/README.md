# Template Model

This is a template for creating new opinion simulation models. It provides a minimal working implementation that satisfies the model interface requirements.

## Directory Structure

```
m00_template/
├── model.py          # Main model implementation
├── components/       # Model components (if needed)
├── data/            # Model-specific data (if needed)
└── README.md        # This file
```

## Usage

1. Copy this template directory to create a new model:
```bash
cp -r src/models/m00_template src/models/mNN_your_model_name
```

2. Rename the model class in `model.py`:
```python
class YourModelName(BaseModel):
    ...
```

3. Implement your model logic:
   - Add necessary components in the `components/` directory
   - Add model-specific data in the `data/` directory
   - Update the model implementation in `model.py`

4. Test your implementation:
```bash
python src/experiment/scripts/validate_model.py \
    --model-path models.mNN_your_model_name.model.YourModelName
```

## Requirements

Your model implementation must:
1. Inherit from `BaseModel`
2. Implement the `simulate_opinions` method
3. Return data in the correct format:
   - Opinion distribution with required fields
   - Sample agents with required attributes
4. Handle the model configuration properly

## Example Output Format

### Opinion Distribution
```json
{
    "summary_statistics": {
        "support": 600,
        "oppose": 300,
        "neutral": 100
    },
    "supporter_reasons": {
        "reason1": 0.7,
        "reason2": 0.3
    },
    "opponent_reasons": {
        "reason1": 0.6,
        "reason2": 0.4
    }
}
```

### Sample Agents
```json
[
    {
        "id": 0,
        "agent": {
            "age": "25-34",
            "income": "50000-75000",
            "education": "bachelor's",
            "occupation": "professional",
            "gender": "female",
            "religion": "none",
            "race": "white"
        },
        "opinion": "support",
        "comment": "Sample comment"
    }
]
``` 