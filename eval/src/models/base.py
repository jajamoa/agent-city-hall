from abc import ABC, abstractmethod
from ..schemas import ZoningProposal, EvaluationResult

class BaseModel(ABC):
    """Base model interface for generating community feedback"""
    
    @abstractmethod
    async def __call__(self, proposal: ZoningProposal) -> EvaluationResult:
        """
        Generate feedback for a proposal
        Args:
            proposal: Input zoning proposal
        Returns:
            EvaluationResult: Generated feedback
        """
        pass 