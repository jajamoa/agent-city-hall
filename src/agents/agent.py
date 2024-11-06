# src/agents/agent.py
from abc import ABC, abstractmethod
from typing import Any
from utils.message_pool import MessagePool
from utils.llm import LLMClient


class Agent(ABC):
    def __init__(self,
                 name: str,
                 data: dict[str, Any],
                 llm_client: LLMClient):               
        self.name = name
        self.data = data
        self.llm_client = llm_client


    @abstractmethod
    def respond(self,
                message_pool: MessagePool,
                **kwargs: Any) -> None:
        pass
