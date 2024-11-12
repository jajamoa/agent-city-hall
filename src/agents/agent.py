# src/agents/agent.py
from abc import ABC, abstractmethod
from typing import Any
from src.utils.message_pool import MessagePool
from src.utils.llm import LLMClient


class Agent(ABC):
    def __init__(self,
                 data: dict[str, Any],
                 llm_client: LLMClient):               
        self.name = data.get("name")
        self.data = data
        self.llm_client = llm_client


    @abstractmethod
    def respond(self,
                message_pool: MessagePool,
                **kwargs: Any) -> None:
        pass
