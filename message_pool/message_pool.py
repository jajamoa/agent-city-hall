import time

class Message:
    def __init__(self, sender_id, content, receiver_id=None, timestamp=None):
        """
        Represents a message exchanged between agents.

        Parameters:
        - sender_id (str): ID of the sender agent.
        - content (str): Content of the message.
        - receiver_id (str): ID of the receiver agent. If None, message is public.
        - timestamp (float): Timestamp of when the message was sent.
        """
        self.sender_id = sender_id
        self.content = content
        self.receiver_id = receiver_id
        self.timestamp = timestamp or time.time()


class MessagePool:
    def __init__(self):
        """
        Initializes an empty message pool.
        """
        self.messages = []

    def add_message(self, sender_id, content, receiver_id=None):
        """
        Adds a message to the pool.

        Parameters:
        - sender_id (str): ID of the agent sending the message.
        - content (str): Content of the message.
        - receiver_id (str): ID of the agent intended to receive the message.
        """
        message = Message(sender_id, content, receiver_id)
        self.messages.append(message)

    def get_observations(self, agent_id):
        """
        Retrieves all messages visible to a specific agent.

        Parameters:
        - agent_id (str): The ID of the agent requesting observations.

        Returns:
        - List[Message]: Messages that the agent can see.
        """
        visible_messages = [
            msg for msg in self.messages
            if msg.receiver_id is None or msg.receiver_id == agent_id
        ]
        return visible_messages

    def clear(self):
        """
        Clears all messages in the pool (useful for starting a new round).
        """
        self.messages = []
