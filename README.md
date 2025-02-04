# Agent City Hall

An agent-based simulation system for evaluating public opinions on urban development proposals.

## Project Structure

```
src/
├── backend/          # Flask-based API service
├── experiment/       # Evaluation framework
│   ├── scripts/     # Experiment runners
│   └── eval/        # Test data and metrics
├── models/          # Simulation models
│   ├── m00_template/  # Model template
│   ├── m01_basic/    # Basic simulation
│   └── m02_stupid/   # LLM-powered agents
└── frontend/        # React-based web interface
```

## Module Relationships

![Architecture Diagram](./assets/architecture_diagram.png)

## Quick Start

1. Install dependencies:
```bash
pip install -e .
cd src/frontend && npm install
```

2. Set up OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

3. Start frontend development server:
```bash
cd src/frontend && npm start
```

## Project Modules

- `backend/`: RESTful API service for proposal evaluation
- `experiment/`: Testing and validation framework
- `models/`: Opinion simulation model implementations
- `frontend/`: React-based web interface for proposal visualization

For detailed documentation, please refer to the README in each module directory.

## License

MIT
