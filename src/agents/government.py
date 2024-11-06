# src/agents/government.py
from typing import Any
from src.agents import Agent
from src.utils import MessagePool
from src.prompts import GOVERNMENT_REPRESENTATIVE_PROMPT_TEMPLATE


class GovernmentDepartmentAgent(Agent):
    def respond(self, message_pool: MessagePool, **kwargs: Any) -> None:
        # 1. prepare data
        department_name = self.data.get("department_name")
        instruction = self.data.get("instruction")
        conversation_history = message_pool.get_conversation()

        # 2. format prompt
        prompt = GOVERNMENT_REPRESENTATIVE_PROMPT_TEMPLATE.format(department_name=department_name, instruction=instruction, conversation_history=conversation_history)

        # 3. get response
        messages = [{"role": "user", "content": prompt}]
        response = self.llm_client.chat(messages)
        message_pool.add_message(self.name, response)
