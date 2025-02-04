# main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Type

from models.base import BaseModel
from models.m01_basic.model import BasicSimulationModel
from models.m02_stupid.model import StupidAgentModel

app = Flask(__name__)
CORS(app)

# Register available models
AVAILABLE_MODELS: Dict[str, Type[BaseModel]] = {
    "basic": BasicSimulationModel,
    "stupid": StupidAgentModel
}

# Initialize default model
DEFAULT_MODEL = "basic"
current_model = AVAILABLE_MODELS[DEFAULT_MODEL]()

@app.route('/set_model', methods=['POST'])
async def set_model():
    """Endpoint to change the active model"""
    data = request.get_json()
    model_name = data.get('model', '').lower()
    
    if not model_name:
        return jsonify({"error": "Model name is required."}), 400
        
    if model_name not in AVAILABLE_MODELS:
        return jsonify({
            "error": f"Unknown model: {model_name}. Available models: {list(AVAILABLE_MODELS.keys())}"
        }), 400
    
    global current_model
    current_model = AVAILABLE_MODELS[model_name]()
    return jsonify({"message": f"Successfully switched to model: {model_name}"})

@app.route('/get_available_models', methods=['GET'])
async def get_available_models():
    """Endpoint to list available models"""
    return jsonify({
        "current_model": next(name for name, cls in AVAILABLE_MODELS.items() 
                            if isinstance(current_model, cls)),
        "available_models": list(AVAILABLE_MODELS.keys())
    })

# API to discuss
@app.route('/discuss', methods=['POST'])
async def discuss():
    data = request.get_json()
    
    # Extract and validate inputs
    region = data.get('region', '').lower()
    population = data.get('population', 0)
    proposal = data.get('proposal', {})
    
    # Validate inputs
    if not region or not isinstance(population, int) or not proposal:
        return jsonify({"error": "Invalid input. Ensure region, population, and proposal are provided."}), 400
    if "title" not in proposal or "description" not in proposal:
        return jsonify({"error": "Invalid proposal. Ensure title and description are provided."}), 400

    try:
        # Run the simulation using the current model
        opinion_distribution, sample_agents = await current_model.simulate_opinions(
            region=region,
            population=population,
            proposal=proposal
        )
        
        # Response structure
        response = {
            "summary": opinion_distribution,
            "comments": sample_agents
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5050)
