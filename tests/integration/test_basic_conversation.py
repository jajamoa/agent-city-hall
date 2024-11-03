# tests/integration/test_basic_conversation.py

from agents.agent_base import AgentBase
from message_pool.message_pool import MessagePool

class SimpleAgent(AgentBase):
    def __init__(self, agent_id, config):
        super().__init__(agent_id, config)

    def make_decision(self):
        if not self.observations:
            # Initial message
            return {"agent_id": self.agent_id, "action": f"Hello from {self.agent_id}!"}
        else:
            # Reply message based on the last observation
            last_observation = self.observations[-1].content
            return {"agent_id": self.agent_id, "action": f"Replying to '{last_observation}'"}

def test_basic_conversation():
    print("\n=== Starting Basic Conversation Test ===")
    
    # Initialize MessagePool and two agents
    message_pool = MessagePool()
    agent1 = SimpleAgent("agent1", config={})
    agent2 = SimpleAgent("agent2", config={})

    # Agent1 sends a message
    decision1 = agent1.make_decision()
    message_pool.add_message(
        sender_id=agent1.agent_id,
        content=decision1["action"]
    )
    print(f"Agent1: {decision1['action']}")

    # Agent2 observes and replies
    agent2.observe(message_pool.get_observations(agent2.agent_id))
    decision2 = agent2.make_decision()
    message_pool.add_message(
        sender_id=agent2.agent_id,
        content=decision2["action"]
    )
    print(f"Agent2: {decision2['action']}")

    # Agent1 observes and replies back
    agent1.observe(message_pool.get_observations(agent1.agent_id))
    decision3 = agent1.make_decision()
    message_pool.add_message(
        sender_id=agent1.agent_id,
        content=decision3["action"]
    )
    print(f"Agent1: {decision3['action']}")

    # Verify the conversation flow
    messages = message_pool.messages
    print("\nFull conversation:")
    for i, msg in enumerate(messages, 1):
        print(f"{i}. {msg.sender_id}: {msg.content}")

    # Assertions
    assert len(messages) == 3, "Expected 3 messages in conversation"
    assert messages[0].content == "Hello from agent1!", "First message should be a greeting"
    assert "Replying to 'Hello from agent1!'" in messages[1].content, "Second message should be a reply to greeting"
    assert "Replying to 'Replying to" in messages[2].content, "Third message should be a reply to the reply"
    
    print("\n✅ All assertions passed!")
    print("=== Test Completed Successfully ===\n")

if __name__ == "__main__":
    test_basic_conversation()
