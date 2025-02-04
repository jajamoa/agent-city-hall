# Experiment Module

Evaluation framework for zoning proposal simulation models.

## Structure

```
experiment/
├── eval/
│   ├── data/
│   │   ├── inputs/       # Input proposals
│   │   └── ground_truth/ # Ground truth data
│   └── utils/
│       ├── data_models.py    # Data structures
│       ├── data_manager.py   # Data I/O
│       └── experiment_utils.py # Experiment utilities
├── log/                  # Experiment results
└── scripts/
    ├── run_experiment.py     # Run experiments
    └── validate_model.py     # Validate models
```

## Usage

### Run Experiment

Run simulation experiments with specified model:

```bash
python src/experiment/scripts/run_experiment.py \
    --name <experiment_name> \
    --model <model_name> \
    --population <num_agents>
```

Example:
```bash
python src/experiment/scripts/run_experiment.py \
    --name test_run \
    --model stupid \
    --population 30
```

### Validate Model

Validate model implementation against required format:

```bash
python src/experiment/scripts/validate_model.py \
    --model-path <model_path> \
    --population <num_agents>
```

Example:
```bash
python src/experiment/scripts/validate_model.py \
    --model-path models.m02_stupid.model.StupidAgentModel \
    --population 30
``` 