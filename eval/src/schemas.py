from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime

class ZoningCell(BaseModel):
    """
    Represents zoning information for a single grid cell in the city map.
    Contains details about building restrictions and location.
    """
    height_limit: int = Field(..., description="Maximum allowed building height in feet")
    category: str = Field(..., description="Land use category (e.g., residential, commercial)")
    last_updated: str = Field(..., description="Timestamp of last modification")
    bbox: Dict[str, float] = Field(..., description="Geographic bounding box coordinates")

class ZoningProposal(BaseModel):
    """
    Complete zoning proposal data structure.
    Contains grid configuration and cell-specific zoning details.
    """
    grid_config: Dict[str, Any] = Field(..., description="Grid system configuration parameters")
    height_limits: Dict[str, Any] = Field(..., description="Available height limit options")
    cells: Dict[str, ZoningCell] = Field(..., description="Mapping of cell IDs to zoning details")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional proposal metadata")

class Opinion(str, Enum):
    """Enumeration of possible opinion types in community feedback"""
    SUPPORT = "support"
    NEUTRAL = "neutral"
    OPPOSE = "oppose"

class Agent(BaseModel):
    """
    Demographic information for a simulated community member.
    Used to generate representative feedback.
    """
    age: str
    income_level: str
    education_level: str
    occupation: str
    gender: str
    religion: Optional[str] = None
    race: Optional[str] = None

class Comment(BaseModel):
    """
    Single feedback comment from a community member.
    Includes demographic information and opinion.
    """
    id: int
    agent: Agent
    opinion: Opinion
    comment: str
    cell_id: str = Field(..., description="ID of the grid cell being commented on")

class EvaluationResult(BaseModel):
    """
    Complete evaluation result for a zoning proposal.
    Includes statistical summary and detailed comments.
    """
    summary: Dict[Opinion, int]
    comments: List[Comment]
    key_themes: Dict[Opinion, List[str]]
    metadata: Optional[Dict[str, Any]] = None

class ExperimentResult(BaseModel):
    """
    Experiment result wrapper with metadata.
    Used to track and compare different evaluation runs.
    """
    timestamp: datetime
    model_name: str
    proposal_id: str
    result: EvaluationResult
    metadata: Optional[Dict[str, Any]] = None 