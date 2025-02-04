from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime

class Opinion(str, Enum):
    """Enumeration of possible opinion types"""
    SUPPORT = "support"
    NEUTRAL = "neutral"
    OPPOSE = "oppose"

class ZoningCell(BaseModel):
    """Zoning information for a single grid cell"""
    height_limit: int
    category: str
    last_updated: str
    bbox: Dict[str, float]

class ZoningProposal(BaseModel):
    """Zoning proposal data structure"""
    grid_config: Dict[str, Any]
    height_limits: Dict[str, Any]
    cells: Dict[str, ZoningCell]
    metadata: Optional[Dict[str, Any]] = None

class Location(BaseModel):
    """Geographic location"""
    lat: float
    lng: float

class Agent(BaseModel):
    """Agent demographic information"""
    age: str
    income_level: str
    education_level: str
    occupation: str
    gender: str
    religion: Optional[str] = None
    race: Optional[str] = None

class Comment(BaseModel):
    """Community feedback comment"""
    id: int
    agent: Agent
    opinion: Opinion
    comment: str
    cell_id: str
    location: Location

class OpinionSummary(BaseModel):
    """Opinion distribution summary"""
    support: int
    neutral: int
    oppose: int

class EvaluationResult(BaseModel):
    """Evaluation result for a proposal"""
    summary: OpinionSummary
    comments: List[Comment]
    key_themes: Optional[Dict[Opinion, List[str]]] = None

class ExperimentResult(BaseModel):
    """Experiment result wrapper"""
    timestamp: datetime
    model_name: str
    proposal_id: str
    result: EvaluationResult 