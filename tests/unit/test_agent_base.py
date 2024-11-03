import unittest
from agents.agent_base import AgentBase

class TestAgentBase(unittest.TestCase):
    def setUp(self):
        # Initialize a simple AgentBase instance for testing
        self.agent = AgentBase(agent_id="agent1", config={})

    def test_observe(self):
        # Test if the agent correctly stores observations
        messages = ["Message 1", "Message 2"]
        self.agent.observe(messages)
        self.assertEqual(self.agent.observations, messages)

    def test_make_decision(self):
        # Test if the agent's default decision is 'noop'
        decision = self.agent.make_decision()
        self.assertEqual(decision['agent_id'], "agent1")
        self.assertEqual(decision['action'], "noop")

    def test_receive_feedback(self):
        # Test if the agent can update its state based on feedback
        feedback = {"key": "value"}
        self.agent.receive_feedback(feedback)
        self.assertIn("key", self.agent.state)
        self.assertEqual(self.agent.state["key"], "value")

if __name__ == "__main__":
    unittest.main()
