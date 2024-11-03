import unittest
from message_pool.message_pool import MessagePool

class TestMessagePool(unittest.TestCase):
    def setUp(self):
        # Initialize an empty MessagePool for testing
        self.message_pool = MessagePool()

    def test_add_message(self):
        # Test if a message is correctly added to the pool
        self.message_pool.add_message(
            sender_id="agent1",
            content="Hello",
            receiver_id=None
        )
        messages = self.message_pool.messages
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Hello")
        self.assertEqual(messages[0].sender_id, "agent1")

    def test_get_observations(self):
        # Test public message visibility
        self.message_pool.add_message(
            sender_id="agent1",
            content="Public Message"
        )
        # Test private message
        self.message_pool.add_message(
            sender_id="agent2",
            content="Private Message",
            receiver_id="agent2"
        )

        # agent1 should only see the public message
        visible_messages_agent1 = self.message_pool.get_observations("agent1")
        self.assertEqual(len(visible_messages_agent1), 1)
        self.assertEqual(visible_messages_agent1[0].content, "Public Message")

        # agent2 should see both messages
        visible_messages_agent2 = self.message_pool.get_observations("agent2")
        self.assertEqual(len(visible_messages_agent2), 2)

    def test_clear(self):
        # Test if the message pool can be cleared
        self.message_pool.add_message(
            sender_id="agent1",
            content="Hello"
        )
        self.assertEqual(len(self.message_pool.messages), 1)
        self.message_pool.clear()
        self.assertEqual(len(self.message_pool.messages), 0)

    def test_message_attributes(self):
        # Test if message attributes are correctly set
        self.message_pool.add_message(
            sender_id="agent1",
            content="Test Message",
            receiver_id="agent2"
        )
        message = self.message_pool.messages[0]
        
        self.assertEqual(message.sender_id, "agent1")
        self.assertEqual(message.content, "Test Message")
        self.assertEqual(message.receiver_id, "agent2")
        self.assertIsNotNone(message.timestamp)

if __name__ == "__main__":
    unittest.main()
