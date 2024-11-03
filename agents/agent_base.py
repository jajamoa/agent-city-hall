class AgentBase:
    def __init__(self, agent_id, config):
        """
        Base class for all agents.

        Parameters:
        - agent_id (str): Unique identifier for the agent.
        - config (dict): Configuration for the agent.
        """
        self.agent_id = agent_id
        self.config = config
        self.state = {}
        self.observations = []

    def observe(self, messages):
        """
        Collect observations from visible messages.

        Parameters:
        - messages (list): List of Message objects visible to this agent.
        """
        self.observations = messages

    def make_decision(self):
        """
        Generate an action/decision based on observations.

        Returns:
        - decision (dict): The decision or action of the agent.
        """
        # Default behavior, to be overridden in subclasses
        decision = {
            "agent_id": self.agent_id,
            "action": "noop"  # No operation by default
        }
        return decision

    def receive_feedback(self, feedback):
        """
        Receive feedback from the environment or other agents.

        Parameters:
        - feedback (dict): Feedback information relevant to the agent.
        """
        self.state.update(feedback)
