# Experiment Module

This directory contains the experiment framework for evaluating agent opinions on zoning proposals.

## Data Flow

![Evaluation Module Data Flow Diagram](../../assets/eval_dataflow.png)

## Directory Structure

```
experiment/
├── protocols/           # Experiment protocols
│   └── sample_protocol.yaml
├── eval/
│   ├── data/
│   │   ├── inputs/     # Input proposals
│   │   └── ground_truth/
│   │       ├── sample_group_distribution_gt.json
│   │       └── sample_individual_gt.json
│   └── utils/          # Evaluation utilities
│       ├── data_manager.py   # Data I/O and management
│       ├── data_models.py    # Data structures
│       └── metrics.py        # Metrics calculation
├── log/                # Experiment results
└── scripts/            # Experiment runners
```

## Running Experiments

To run an experiment:

```bash
python scripts/run_experiment.py --protocol protocols/sample_protocol.yaml
```

Results will be in `log/{experiment_name}_{timestamp}/`.

## Validating Models

Before running experiments, you can validate your model implementation:

```bash
python scripts/validate_model.py \
    --model-path models.mNN_your_model_name.model.YourModelName \
    --population 3
```

The validator will:
1. Load your model class
2. Run a sample simulation
3. Verify the output format and data types
4. Check if agent ages are valid integers (18-85)

### Example

```bash
# Validate basic model
python scripts/validate_model.py --model-path models.m02_stupid.model.StupidAgentModel --population 3
```

Expected output:
```
✓ Model loaded successfully
✓ Simulation completed
✓ All validation checks passed
```

## Protocol Format

Protocols define experiment parameters in YAML format:

```yaml
name: "experiment_name"
description: "Experiment description"

model: "stupid"    # which model to use for simulation
population: 2      # number of agents to simulate

input:
  proposals:       # list of input proposal files
    - "sample_proposal.json"

region: "san_francisco"    # target region

evaluation:
  metrics:
    - type: "group_distribution"
      ground_truth: "sample_group_distribution_gt.json"
    - type: "individual_match"
      ground_truth: "sample_individual_gt.json"
```

## Statistical Metrics

The evaluation uses three distance metrics to compare opinion distributions:

- **Jensen-Shannon Divergence**: A symmetric and bounded measure of similarity between probability distributions, defined as $\sqrt{\frac{D_{KL}(P\|M) + D_{KL}(Q\|M)}{2}}$ where $M=\frac{P+Q}{2}$ ([wiki](https://en.wikipedia.org/wiki/Jensen%E2%80%93Shannon_divergence))

- **Chi-square Distance**: A weighted sum of squared differences between observed and expected frequencies, defined as $\sum \frac{(O_i - E_i)^2}{E_i}$ ([wiki](https://en.wikipedia.org/wiki/Chi-squared_test))

- **Total Variation Distance**: Half the L1 distance between two probability distributions, defined as $\frac{1}{2}\sum|P(x) - Q(x)|$ ([wiki](https://en.wikipedia.org/wiki/Total_variation_distance_of_probability_measures))

## Output Structure

Each experiment run creates a directory under `log/` with:

- `protocol.yaml`: Copy of the experiment protocol
- `experiment_metadata.json`: Runtime information
- For each proposal:
  - `{id}_input.json`: Input proposal
  - `{id}_output.json`: Simulation results
  - `{id}_metrics.json`: Evaluation metrics (if ground truth exists)