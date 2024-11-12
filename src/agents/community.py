# src/agents/community_member.py
from typing import Any
from src.agents import Agent
from src.utils import MessagePool
from src.prompts import COMMUNITY_MEMBER_PROMPT_TEMPLATE


class CommunityMemberAgent(Agent):
    def respond(self, message_pool: MessagePool, **kwargs: Any) -> None:
        # 1. prepare data
        role = self.data["role"]
        instruction = self.data["instruction"]
        conversation_history = message_pool.get_conversation()

        # 2. format prompt
        prompt = COMMUNITY_MEMBER_PROMPT_TEMPLATE.format(role=role, instruction=instruction, conversation_history=conversation_history)

        # 3. get response
        messages = [{"role": "user", "content": prompt}]
        response = self.llm_client.chat(messages)
        message_pool.add_message(self.name, response)
