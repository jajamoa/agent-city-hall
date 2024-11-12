# src/utils/message_pool.py
from typing import List, Dict


class MessagePool:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, agent_name: str, message: str) -> None:
        self.messages.append({'agent': agent_name, 'message': message})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages.copy()

    def clear_pool(self) -> None:
        self.messages = []

    def get_conversation(self) -> List[Dict[str, str]]:
        # Returns the entire conversation history
        return self.get_messages()
    
    def log_conversation(self, filename: str) -> None:
        # Logs the conversation history to a file
        with open(filename, 'w') as f:
            for message in self.get_messages():
                f.write(f"{message['agent']}: {message['message']}\n")
            f.write("\n")