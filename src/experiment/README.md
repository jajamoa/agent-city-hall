# Experiment Module

Tools and scripts for evaluating opinion simulation models.

## Features

- Model validation framework
- Batch experiment runner
- Ground truth comparison tools
- Standardized input/output formats

## Directory Structure

```
experiment/
├── scripts/           # Experiment scripts
│   ├── validate_model.py    # Model validation
│   └── run_experiment.py    # Batch experiment runner
├── eval/              # Evaluation assets
│   ├── data/         # Test data
│   │   ├── inputs/   # Input proposals
│   │   └── ground_truth/  # Ground truth data
└── log/              # Experiment outputs
```

## Usage

```bash
# Validate a model
python src/experiment/scripts/validate_model.py \
    --model-path models.m02_stupid.model.StupidAgentModel \
    --population 30

# Run batch experiment
python src/experiment/scripts/run_experiment.py \
    --name test_run \
    --model stupid \
    --population 30
``` 