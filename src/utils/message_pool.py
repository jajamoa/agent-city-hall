from typing import List, Dict, Optional
import os
from datetime import datetime


class MessagePool:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add_message(self, agent_name: str, message: str, recipient: Optional[str] = None) -> None:
        """Add a message to the pool with timestamp"""
        self.messages.append({
            'agent': agent_name,
            'recipient': recipient,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

    def get_messages(self, recipient: Optional[str] = None) -> List[Dict[str, str]]:
        """Get messages, optionally filtered by recipient"""
        if recipient is None:
            return self.messages.copy()
        
        return [
            msg for msg in self.messages 
            if msg['recipient'] is None or msg['recipient'] == recipient
        ]

    def clear_pool(self) -> None:
        """Clear all messages"""
        self.messages = []

    def get_conversation(self) -> List[Dict[str, str]]:
        """Get full conversation history"""
        return self.messages.copy()

    def log_conversation(self, filename: str) -> None:
        """Log conversation to file"""
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        try:
            with open(filename, 'w') as f:
                for message in self.get_messages():
                    recipient_info = f" -> {message['recipient']}" if message['recipient'] else " (broadcast)"
                    timestamp = message['timestamp']
                    f.write(f"[{timestamp}] {message['agent']}{recipient_info}: {message['message']}\n")
        except Exception as e:
            print(f"Error logging conversation: {e}")