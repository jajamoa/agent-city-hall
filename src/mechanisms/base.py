# src/mechanisms/base.py
from abc import ABC, abstractmethod
from typing import List
from src.agents.agent import Agent
from src.utils import LLMClient, MessagePool

class BaseFlow(ABC):
    def __init__(self, output_file: str):
        self.output_file = output_file
        self.llm_client = LLMClient()
        self.message_pool = MessagePool()

    @abstractmethod
    def start_flow(self) -> None:
        pass
