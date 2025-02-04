# Backend Service

This is the backend service for the Agent City Hall project. It provides APIs for simulating public opinions on urban development proposals.

## Architecture

The backend is built with a modular architecture that supports multiple opinion simulation models:

```
src/
├── backend/          # Backend service
│   ├── main.py      # API endpoints
│   └── utils/       # Utility functions
└── models/          # Opinion simulation models
    ├── base.py      # Base model interface
    └── basic_simulation/  # Basic simulation model
        ├── model.py      # Model implementation
        ├── components/   # Model components
        └── data/        # Model-specific data
```

## Available Models

The service supports multiple opinion simulation models that can be switched at runtime:

- `basic`: Basic simulation model using demographic-based agent simulation
- More models coming soon...

## API Endpoints

### Model Management

#### GET /get_available_models
Get the list of available models and current active model.

Response:
```json
{
    "current_model": "basic",
    "available_models": ["basic"]
}
```

#### POST /set_model
Change the active model.

Request:
```json
{
    "model": "basic"
}
```

Response:
```json
{
    "message": "Successfully switched to model: basic"
}
```

### Opinion Simulation

#### POST /discuss
Simulate public opinions on a proposal.

Request:
```json
{
    "region": "boston",
    "population": 1000,
    "proposal": {
        "title": "New Park Project",
        "description": "Proposal to build a new park..."
    }
}
```

Response:
```json
{
    "summary": {
        "summary_statistics": {
            "support": 600,
            "oppose": 300,
            "neutral": 100
        },
        "supporter_reasons": {...},
        "opponent_reasons": {...}
    },
    "comments": [
        {
            "id": 0,
            "agent": {
                "age": "25-34",
                "income": "50000-75000",
                ...
            },
            "opinion": "support",
            "comment": "..."
        },
        ...
    ]
}
```

## Running the Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python src/backend/main.py
```

The service will start on `http://localhost:5050`. 