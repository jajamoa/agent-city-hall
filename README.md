
# Agent City Hall

Agent City Hall serves as the human layer for existing city simulations, introducing social alignment to the model. This framework integrates diverse agents—such as government, developers, and residents—to enable social dynamics modeling and policy evaluation, enriching urban planning simulations with a focus on human-centric perspectives.

## Project Structure

- **main.py**: Main script to initialize and run the simulation.
- **config/**: Contains configuration files, such as `config.yaml`, for setting parameters.
- **agents/**: Defines different types of agents involved in the simulation.
  - `agent_base.py`: Base class for agents.
  - `government_agent.py`: Government agent class.
  - `developer_agent.py`: Developer agent class.
  - `resident_agent.py`: Resident agent class.
- **interaction/**: Manages interactions among agents.
- **message_pool/**: Manages the message exchange between agents.
- **alignment/**: Contains the pluralistic alignment module.
- **backends/**: Contains different intelligence backend implementations.
- **utils/**: Utility functions and helpers.
- **tests/**: Contains all test files.
  - `unit/`: Unit tests for individual components.
  - `integration/`: Integration tests for component interactions.

![Architecture Diagram](./images/architecture_diagram.png)

## Getting Started

1. **Install Dependencies**: Make sure to install the required packages.
   ```bash
   pip install -r requirements.txt
   ```

2. **Development Setup**: Install package in development mode.
    ```bash
    pip install -e .

    # This allows you to:
    # - Import modules from anywhere
    # - Modify code without reinstalling
    # - Run tests properly
    ```

3. **Run the Simulation**:
   ```bash
   python main.py
   ```

## Testing

Run tests from the project root directory:

```bash
# Run specific test
pytest tests/unit/test_agent_base.py

# Run all tests
pytest tests/unit/       # unit tests
pytest tests/integration/    # integration tests
pytest                  # all tests
```

## Requirements

The project dependencies are listed in `requirements.txt`.

## License

This project is licensed under the MIT License.
