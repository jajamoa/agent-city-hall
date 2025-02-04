# Agent City Hall

An agent-based simulation system for evaluating public opinions on urban development proposals.

## Features

- Agent-based opinion simulation with demographic considerations
- LLM-powered agent reasoning and comment generation
- RESTful API for proposal evaluation
- Comprehensive experiment and validation framework

## Project Structure

```
src/
├── backend/          # Flask-based API service
├── experiment/       # Evaluation framework
│   ├── scripts/     # Experiment runners
│   └── eval/        # Test data and metrics
└── models/          # Simulation models
    ├── m00_template/  # Model template
    ├── m01_basic/    # Basic simulation
    └── m02_stupid/   # LLM-powered agents
```

## Quick Start

1. Install dependencies:
```bash
pip install -e .
```

2. Set up OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

3. Run model validation:
```bash
python src/experiment/scripts/validate_model.py \
    --model-path models.m02_stupid.model.StupidAgentModel
```

4. Start backend service:
```bash
python src/backend/app.py
```

## Development

- Use the model template in `src/models/m00_template/` for new models
- Run experiments with `src/experiment/scripts/run_experiment.py`
- Test models with `src/experiment/scripts/validate_model.py`

## License

MIT
