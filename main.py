# main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.demographics import DemographicsSearchEngine
from src.simulation import SimulationEngine

app = Flask(__name__)
CORS(app)


# API to lookup demographics
@app.route('/lookup_demographics', methods=['POST'])
def lookup_demographics():
    region = request.args.get('region', '').lower()
    if not region:
        return jsonify({"error": "Region parameter is required."}), 400
    try:
        demographics = demographics_search_engine.search(region)
        return jsonify({"region": region, "demographics": demographics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to discuss
@app.route('/discuss', methods=['POST'])
def discuss():
    data = request.get_json()
    
    # Extract and validate inputs
    region = data.get('region', '').lower()
    population = data.get('population', 0)
    proposal = data.get('proposal', {})
    demographics = data.get('demographics', {})
    
    # Validate inputs and check for missing values
    if not region or not isinstance(population, int) or not proposal or not demographics:
        return jsonify({"error": "Invalid input. Ensure region, population, proposal, and demographics are provided."}), 400
    if "title" not in proposal or "description" not in proposal:
        return jsonify({"error": "Invalid proposal. Ensure title and description are provided."}), 400

    # Run the simulation
    opinion_distribution, sample_agents = simulation_engine.simulate(region, population, proposal, demographics)
    
    # Response structure
    response = {
        "summary": opinion_distribution,
        "comments": sample_agents
    }

    return jsonify(response)

if __name__ == '__main__':
    # Initialize the demographics search engine
    demographics_search_engine = DemographicsSearchEngine()
    # Initialize the simulation engine
    simulation_engine = SimulationEngine()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5050)
