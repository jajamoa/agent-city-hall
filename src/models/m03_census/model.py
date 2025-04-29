import json
import os
import random
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

from ..base import BaseModel, ModelConfig
from .components.llm import OpenAILLM

# Default grid bounds (San Francisco area)
DEFAULT_GRID_BOUNDS = {
    "north": 37.8120,
    "south": 37.7080,
    "east": -122.3549,
    "west": -122.5157
}

# Reason mapping
REASON_MAPPING = {
    "Housing supply and availability": "A",
    "Affordability for low- and middle-income residents": "B",
    "Impact on neighborhood character": "C",
    "Infrastructure and services capacity": "D",
    "Economic development and job creation": "E",
    "Environmental concerns": "F",
    "Transit and transportation access": "G",
    "Displacement of existing residents": "H",
    "Equity and social justice": "I",
    "Public space and amenities": "J",
    "Property values and investment": "K",
    "Historical preservation": "L"
}

# Scenario mapping (for translating proposal IDs to scenario IDs)
SCENARIO_MAPPING = {
    "proposal_000": "1.1",
    "proposal_001": "1.2",
    "proposal_002": "1.3",
    "proposal_003": "2.1",
    "proposal_004": "2.2",
    "proposal_005": "2.3",
    "proposal_006": "3.1",
    "proposal_007": "3.2",
    "proposal_008": "3.3"
}

class Census(BaseModel):
    """A model that generates opinions using OpenAI API and agent data from a JSON file."""
    
    def __init__(self, config: ModelConfig = None):
        """Initialize model components and set the path to the agent data JSON file.
        
        Args:
            config: Model configuration containing settings such as population and agent_data_file.
        """
        super().__init__(config)
        self.llm = OpenAILLM()
        
        # Get custom OpenAI parameters if provided
        self.temperature = getattr(self.config, "temperature", 0.7)
        self.max_tokens = getattr(self.config, "max_tokens", 800)
        
        # Load the agent file
        self.agent_data_file = getattr(
            self.config, 
            "agent_data_file", 
            os.path.join(os.path.dirname(__file__), "census_data", "agents_37.json")
        )
        
        print(f"DEBUG Census.__init__: agent_data_file={self.agent_data_file}")
        
        # Track which proposal we're currently processing (for scenario ID mapping)
        self.current_proposal_id = None
    
    async def simulate_opinions(self,
                               region: str,
                               proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate opinions using OpenAI based on agent information from a JSON file.
        
        Args:
            region: The target region name.
            proposal: A dictionary containing the rezoning proposal details.
        
        Returns:
            A dictionary with participant IDs as keys, each containing opinions and reasons.
            Output format:
            {
                "<participant_id>": {
                    "opinions": {
                        "<scenario_id>": <rating_1_to_10>,
                        ...
                    },
                    "reasons": {
                        "<scenario_id>": ["A", "C", "D"],
                        ...
                    }
                },
                ...
            }
        """
        # Extract proposal ID from metadata if available
        self.current_proposal_id = proposal.get("proposal_id", None)
        print(f"DEBUG simulate_opinions: Processing proposal_id={self.current_proposal_id}")
        
        # Extract grid bounds and height limits info
        grid_bounds = proposal.get("gridConfig", {}).get("bounds", DEFAULT_GRID_BOUNDS)
        height_limits = proposal.get("heightLimits", {})
        
        # Prepare readable description of the proposal
        proposal_desc = self._create_proposal_description(proposal)
        print(f"DEBUG: Generated proposal description: {proposal_desc[:100]}...")
        
        # Verify agent_data_file exists
        if not os.path.exists(self.agent_data_file):
            print(f"ERROR: Agent data file not found: {self.agent_data_file}")
            # Generate mock data for testing/debugging
            return self._generate_mock_results()
        
        # Load agents from JSON file
        print(f"DEBUG: Loading agents from: {self.agent_data_file}")
        try:
            with open(self.agent_data_file, 'r', encoding='utf-8') as f:
                raw_agents = json.load(f)
            
            print(f"DEBUG: Loaded {len(raw_agents)} agents")
        except Exception as e:
            print(f"ERROR: Failed to load agents: {str(e)}")
            # Generate mock data for testing/debugging
            return self._generate_mock_results()
        
        results = {}
        
        # Process each agent (limit to 3 for testing if needed)
        # raw_agents = raw_agents[:3]  # Uncomment to process only 3 agents for testing
        
        for i, raw_agent in enumerate(raw_agents):
            participant_id = raw_agent.get("id")
            if not participant_id:
                participant_id = f"agent_{i:03d}"
                
            print(f"DEBUG: Processing agent {i+1}/{len(raw_agents)}: {participant_id}")
            
            # Generate opinion and reasons for this proposal
            try:
                opinion_data = await self._generate_opinion(
                    raw_agent, 
                    proposal,
                    proposal_desc,
                    region
                )
                results[participant_id] = opinion_data
            except Exception as e:
                print(f"ERROR: Failed to generate opinion for agent {participant_id}: {str(e)}")
                # Generate fallback data for this agent
                results[participant_id] = self._generate_fallback_opinion(
                    SCENARIO_MAPPING.get(self.current_proposal_id, "1.1")
                )
        
        print(f"DEBUG: Completed processing {len(results)} agents")
        return results
    
    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing/debugging purposes."""
        print("DEBUG: Generating mock results for testing")
        
        scenario_id = SCENARIO_MAPPING.get(self.current_proposal_id, "1.1")
        results = {}
        
        # Generate 5 mock agents
        for i in range(5):
            agent_id = f"mock_agent_{i:03d}"
            rating = random.randint(3, 9)
            num_reasons = random.randint(1, 3)
            reason_codes = random.sample(list(REASON_MAPPING.values()), num_reasons)
            
            results[agent_id] = {
                "opinions": {
                    scenario_id: rating
                },
                "reasons": {
                    scenario_id: reason_codes
                }
            }
        
        return results
    
    def _create_proposal_description(self, proposal: Dict[str, Any]) -> str:
        """Create a human-readable description of a rezoning proposal.
        
        Args:
            proposal: A dictionary containing proposal details.
            
        Returns:
            A string describing the key elements of the proposal.
        """
        # Extract basic information
        height_limits = proposal.get("heightLimits", {})
        default_height = height_limits.get("default", "varies")
        grid_config = proposal.get("gridConfig", {})
        cell_size = grid_config.get("cellSize", 100)
        
        # Count zones by category
        cells = proposal.get("cells", {})
        zone_counts = {}
        
        try:
            for cell_id, cell in cells.items():
                category = cell.get("category", "unknown")
                height = cell.get("heightLimit", default_height)
                
                key = f"{category}_{height}"
                zone_counts[key] = zone_counts.get(key, 0) + 1
        except Exception as e:
            print(f"ERROR: Failed to count zones: {str(e)}")
            # Return a simplified description if zone counting fails
            return f"Rezoning proposal with {cell_size}m cells. Default height limit: {default_height} feet."
        
        # Create description
        desc = f"Rezoning proposal with {cell_size}m cells and {len(cells)} modified zones. "
        desc += f"Default height limit: {default_height} feet. "
        
        # Add zone category information if available
        if zone_counts:
            desc += "Zones include: "
            zone_info = []
            for key, count in zone_counts.items():
                try:
                    category, height = key.split("_")
                    zone_info.append(f"{count} {category} zones (height: {height}ft)")
                except:
                    zone_info.append(f"{count} zones of type {key}")
            desc += ", ".join(zone_info[:3])  # Limit to 3 zone types to keep it concise
            if len(zone_info) > 3:
                desc += f", and {len(zone_info) - 3} more zone types"
        
        return desc
    
    async def _generate_opinion(self, 
                              agent: Dict[str, Any], 
                              proposal: Dict[str, Any],
                              proposal_desc: str,
                              region: str) -> Dict[str, Any]:
        """Generate opinion and reasons for a proposal for a specific agent.
        
        Args:
            agent: A dictionary containing agent demographic data.
            proposal: A dictionary containing the rezoning proposal details.
            proposal_desc: A human-readable description of the proposal.
            region: The target region name.
            
        Returns:
            A dictionary with opinions and reasons.
        """
        # Get scenario ID from proposal ID or use a default
        scenario_id = "1.1"  # Default scenario ID
        if self.current_proposal_id and self.current_proposal_id in SCENARIO_MAPPING:
            scenario_id = SCENARIO_MAPPING[self.current_proposal_id]
        
        print(f"DEBUG: Generating opinion for scenario_id={scenario_id}")
        
        # Build prompt based on proposal and agent details
        prompt = self._build_opinion_prompt(agent, proposal_desc, region)
        print(f"DEBUG: Prompt length: {len(prompt)} characters")
        
        # Skip actual LLM call for testing if needed
        # return self._generate_fallback_opinion(scenario_id)
        
        # Generate response from LLM
        try:
            response = await self.llm.generate(
                prompt, 
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            print(f"DEBUG: Received response of length {len(response)} characters")
        except Exception as e:
            print(f"ERROR: LLM generation failed: {str(e)}")
            return self._generate_fallback_opinion(scenario_id)
        
        try:
            # Parse the response to extract rating and reasons
            rating, reasons = self._parse_opinion_response(response)
            print(f"DEBUG: Extracted rating={rating}, reasons={reasons}")
            
            # Format into the expected output structure
            return {
                "opinions": {
                    scenario_id: rating
                },
                "reasons": {
                    scenario_id: reasons
                }
            }
        except Exception as e:
            print(f"ERROR: Failed to parse response: {str(e)}")
            # Generate fallback random data
            return self._generate_fallback_opinion(scenario_id)
    
    def _build_opinion_prompt(self, 
                             agent: Dict[str, Any], 
                             proposal_desc: str,
                             region: str) -> str:
        """Build a prompt for generating opinions on a housing policy proposal.
        
        Args:
            agent: A dictionary containing agent demographic data.
            proposal_desc: A human-readable description of the proposal.
            region: The target region name.
            
        Returns:
            A string containing the prompt for the LLM.
        """
        # Handle possible different agent data formats
        agent_data = {}
        if "agent" in agent and isinstance(agent["agent"], dict):
            agent_data = agent["agent"]
        elif isinstance(agent, dict):
            agent_data = agent
        
        prompt = f"""As a resident of {region} with the following characteristics, rate your opinion on the proposed housing policy change and provide reasons for your stance.

Resident Information:
- Age: {agent_data.get('age', 'unknown')}
- Income: {agent_data.get('income', 'unknown')}
- Occupation: {agent_data.get('occupation', 'unknown')}
- Housing Status: {agent_data.get('householder type', 'unknown')}
- Transportation: {agent_data.get('means of transportation', 'unknown')}
- Family Type: {agent_data.get('family type', 'unknown')}

Housing Policy Proposal:
{proposal_desc}

Consider how this proposal might affect:
- Housing availability and affordability 
- Neighborhood character and livability
- Infrastructure and public services
- Economic development and property values
- Environmental impact
- Equity and displacement issues

Provide:
1. A rating from 1-10 (where 1=strongly oppose, 5=neutral, 10=strongly support)
2. 1-3 main reasons for your opinion using ONLY the codes below:

Reason Codes:
A: Housing supply and availability
B: Affordability for low- and middle-income residents
C: Impact on neighborhood character
D: Infrastructure and services capacity
E: Economic development and job creation
F: Environmental concerns
G: Transit and transportation access
H: Displacement of existing residents
I: Equity and social justice
J: Public space and amenities
K: Property values and investment
L: Historical preservation

Format your response EXACTLY as follows:
Rating: 7
Reasons: A,C,D

Remember to:
- Use ONLY the letter codes provided (A through L)
- Include 1-3 reason codes
- Maintain the exact format specified
"""
        
        return prompt
    
    def _parse_opinion_response(self, response: str) -> Tuple[int, List[str]]:
        """Parse the LLM response to extract rating and reason codes.
        
        Args:
            response: The response from the LLM.
            
        Returns:
            A tuple of (rating, reason_codes).
        """
        rating = 5  # Default neutral rating
        reasons = []
        
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            
            # Extract rating
            if line.lower().startswith("rating:"):
                try:
                    rating_str = line.split(":", 1)[1].strip()
                    rating = int(rating_str)
                    # Ensure rating is in the 1-10 range
                    rating = max(1, min(10, rating))
                except:
                    pass
            
            # Extract reason codes
            elif line.lower().startswith("reasons:"):
                try:
                    reasons_str = line.split(":", 1)[1].strip()
                    reasons = [code.strip() for code in reasons_str.split(",")]
                    # Filter out any invalid codes
                    valid_codes = set(REASON_MAPPING.values())
                    reasons = [code for code in reasons if code in valid_codes]
                except:
                    pass
        
        # If no reasons were extracted, generate random ones
        if not reasons:
            num_reasons = random.randint(1, 3)
            reasons = random.sample(list(REASON_MAPPING.values()), num_reasons)
        
        return rating, reasons
    
    def _generate_fallback_opinion(self, scenario_id: str) -> Dict[str, Any]:
        """Generate a fallback random opinion and reasons for a scenario.
        
        Args:
            scenario_id: The ID of the scenario.
            
        Returns:
            A dictionary with random opinions and reasons.
        """
        # Generate random rating between 1 and 10
        rating = random.randint(3, 9)
        
        # Generate 1-3 random reason codes
        num_reasons = random.randint(1, 3)
        reason_codes = random.sample(list(REASON_MAPPING.values()), num_reasons)
        
        return {
            "opinions": {
                scenario_id: rating
            },
            "reasons": {
                scenario_id: reason_codes
            }
        }
