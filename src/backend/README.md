# Backend Service

A Flask-based backend service for the Agent City Hall project.

## Features

- RESTful API for zoning proposal management
- Real-time opinion simulation using configurable agent models
- CORS support for frontend integration

## API Endpoints

- `GET /health`: Health check endpoint
- `POST /set_model`: Switch between different simulation models
- `POST /simulate`: Run opinion simulation for a given proposal

## Usage

```bash
# Start the backend service
python src/backend/app.py
```

The service will be available at `http://localhost:5050`. 