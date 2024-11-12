# src/agents/developer.py
from typing import Any
from src.agents import Agent
from src.utils import MessagePool
from src.prompts import DEVELOPER_STAGE_1_PROMPT_TEMPLATE, DEVELOPER_STAGE_2_PROMPT_TEMPLATE


class DeveloperAgent(Agent):
    def respond(self, message_pool: MessagePool, stage: str) -> None:
        # 1. prepare data
        development_proposal = self.data["development_proposal"]
        conversation_history = message_pool.get_conversation()

        # 2. format prompt
        if stage == "opening":
            prompt = DEVELOPER_STAGE_1_PROMPT_TEMPLATE.format(development_proposal=development_proposal)
        elif stage == "conclusion":
            prompt = DEVELOPER_STAGE_2_PROMPT_TEMPLATE.format(development_proposal=development_proposal, conversation_history=conversation_history)
        else:
            raise ValueError(f"Unknown stage '{stage}'. Available stages: [opening, conclusion].")

        # 3. get response
        messages = [{"role": "user", "content": prompt}]
        response = self.llm_client.chat(messages)
        message_pool.add_message(self.name, response)
