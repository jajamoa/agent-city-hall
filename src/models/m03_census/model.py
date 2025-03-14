import json
import os
import random
from pathlib import Path
from typing import Dict, Any, Tuple, List

from ..base import BaseModel, ModelConfig
from .components.llm import OpenAILLM

# Default grid bounds (San Francisco area)
DEFAULT_GRID_BOUNDS = {
    "north": 37.8120,
    "south": 37.7080,
    "east": -122.3549,
    "west": -122.5157
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
        # load the agent file
        self.agent_data_file = getattr(
            self.config, 
            "agent_data_file", 
            # r"G:\ACH\agent-city-hall\src\models\m03_census\census_data\agents_37.json"
            os.path.join(os.path.dirname(__file__), "census_data", "agents_37.json")

        )
    
    async def simulate_opinions(self,
                                region: str,
                                proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate opinions using OpenAI based on agent information from a JSON file.
        
        Args:
            region: The target region name.
            proposal: A dictionary containing the rezoning proposal details, including grid_config and cells.
        
        Returns:
            A dictionary with opinion summary, detailed comments, and key themes.
            Output format:
            {
                "summary": {
                    "support": int,
                    "neutral": int,
                    "oppose": int
                },
                "comments": [
                    {
                        "id": int,
                        "agent": { 原始demographic数据 },
                        "location": {
                            "lat": float,
                            "lng": float
                        },
                        "cell_id": str,
                        "opinion": str,
                        "comment": str
                    },
                    ...
                ],
                "key_themes": {
                    "support": [str, ...],
                    "oppose": [str, ...]
                }
            }
        """
        # Use grid bounds from proposal if provided, else default bounds
        grid_bounds = proposal.get("grid_config", {}).get("bounds", DEFAULT_GRID_BOUNDS)
        print("data file", self.agent_data_file)
        # Load agents from JSON file
        with open(self.agent_data_file, 'r', encoding='utf-8') as f:
            raw_agents = json.load(f)
        
        agents = []
        opinion_counts = {"support": 0, "oppose": 0, "neutral": 0}
        key_themes = {"support": set(), "oppose": set()}
        
        for raw_agent in raw_agents:
            # Generate opinion, comment, and key themes using OpenAI
            opinion, comment, themes = await self._generate_opinion_and_comment(raw_agent, proposal)
            opinion_counts[opinion] += 1
            
            # Determine the nearest cell for the agent based on coordinates
            agent_lat = raw_agent['coordinates']['lat']
            agent_lng = raw_agent['coordinates']['lng']
            nearest_cell = None
            min_distance = float('inf')
            nearest_cell_id = None
            
            for cell_id, cell in proposal['cells'].items():
                bbox = cell['bbox']
                cell_lat = (bbox['north'] + bbox['south']) / 2
                cell_lng = (bbox['east'] + bbox['west']) / 2
                distance = ((agent_lat - cell_lat) ** 2 + (agent_lng - cell_lng) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    nearest_cell = cell
                    nearest_cell_id = cell_id
            
            # Build agent info using the original demographic data from JSON
            agent_info = {
                "id": raw_agent.get("id"),
                "agent": raw_agent.get("agent", {}), 
                "location": {
                    "lat": raw_agent["coordinates"]["lat"],
                    "lng": raw_agent["coordinates"]["lng"]
                },
                "cell_id": nearest_cell_id,
                "opinion": opinion,
                "comment": comment
            }
            agents.append(agent_info)
            
            # Update key themes from the generated response
            if themes:
                key_themes[opinion].update(themes)
        
        return {
            "summary": opinion_counts,
            "comments": agents,
            "key_themes": {
                "support": list(key_themes["support"]),
                "oppose": list(key_themes["oppose"])
            }
        }
    
    async def _generate_opinion_and_comment(self, agent: Dict[str, Any], proposal: Dict[str, Any]) -> Tuple[str, str, List[str]]:
        """Generate opinion and comment for an agent using OpenAI.
        
        This function builds a prompt using agent and proposal details,
        then calls the LLM to generate an opinion (support/oppose/neutral),
        a brief comment, and key themes.
        
        Returns:
            A tuple of (opinion, comment, themes).
        """
        agent_lat = agent['coordinates']['lat']
        agent_lng = agent['coordinates']['lng']
        nearest_cell = None
        min_distance = float('inf')
        
        for cell_id, cell in proposal['cells'].items():
            bbox = cell['bbox']
            cell_lat = (bbox['north'] + bbox['south']) / 2
            cell_lng = (bbox['east'] + bbox['west']) / 2
            distance = ((agent_lat - cell_lat) ** 2 + (agent_lng - cell_lng) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest_cell = cell
        
        prompt = f"""Given a rezoning proposal and a resident's information, generate their opinion and a brief comment.

Proposal Details:
- Nearest Rezoning Area: A {nearest_cell['category']} zone with height limit changed to {nearest_cell['height_limit']} feet
- Distance from Resident: {min_distance:.4f} degrees (approximately {min_distance * 111:.1f} km)
- Default Height Limit: {proposal['height_limits']['default']} feet

Resident Information:
- Location: ({agent['coordinates']['lat']}, {agent['coordinates']['lng']})
- Age: {agent['agent'].get('age')}
- Income: {agent['agent'].get('income', '')}
- Education: {agent['agent'].get('education', 'bachelor')}
- Occupation: {agent['agent'].get('occupation', '')}
- Gender: {agent['agent'].get('gender', 'unknown')}

Consider how the height limit change and distance from the rezoning area might affect the resident's daily life, property value, and community character.

Generate:
1. Opinion (support/oppose/neutral)
2. A brief comment explaining their stance (1-2 sentences)
3. Key themes in the comment (2-3 keywords)

Format: opinion|comment|theme1,theme2,theme3"""
        
        response = await self.llm.generate(prompt)
        try:
            parts = response.strip().split("|")
            if len(parts) >= 3:
                opinion, comment, themes = parts[:3]
                themes = [theme.strip() for theme in themes.split(",")]
            else:
                opinion, comment = parts[:2]
                themes = []
            opinion = opinion.strip().lower()
            if opinion not in {"support", "oppose", "neutral"}:
                opinion = random.choice(["support", "oppose", "neutral"])
            return opinion, comment.strip(), themes
        except Exception as e:
            opinion = random.choice(["support", "oppose", "neutral"])
            comment = f"Error processing response: {str(e)}"
            return opinion, comment, []
