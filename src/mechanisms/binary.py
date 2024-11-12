# src/mechanisms/binary.py

import yaml
import logging
from typing import Dict
from src.agents import DeveloperAgent, GovernmentDepartmentAgent, CommunityMemberAgent
from src.utils import MessagePool
from src.mechanisms import BaseFlow

logging.basicConfig(level=logging.INFO)

class BinaryFlow(BaseFlow):
    def __init__(self, 
                 config_path: str = "config.yaml", 
                 output_file: str = "conversation_log.txt"):
        super().__init__(output_file)
        self.config_path = config_path
        self.output_file = output_file
        self.message_pool = MessagePool()
        self.agents = self._initialize_agents()

    def _load_agent_data(self) -> Dict:
        try:
            with open(self.config_path, "r") as file:
                agent_data = yaml.load(file, Loader=yaml.FullLoader)
            logging.info("Configuration loaded successfully.")
            return agent_data["agents"]
        except FileNotFoundError:
            logging.error(f"Configuration file {self.config_path} not found.")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file: {e}")
            raise

    def _initialize_agents(self) -> Dict[str, BaseFlow]:
        agent_data = self._load_agent_data()
        
        developer_data = agent_data["developer"]
        government_data = agent_data["government"]
        citizen_data = agent_data["citizens"]
        
        agents = {
            "developer": DeveloperAgent(developer_data, self.llm_client),
            "government": GovernmentDepartmentAgent(government_data, self.llm_client),
            **{f"citizen_{i}": CommunityMemberAgent(citizen_data[key], self.llm_client) for i, key in enumerate(citizen_data)}
        }
        logging.info("Agents initialized successfully.")
        return agents

    def _developer_intro(self):
        logging.info("Developer providing project overview.")
        self.agents["developer"].respond(self.message_pool, stage="opening")

    def _collect_citizen_feedback(self):
        logging.info("Collecting feedback from community members.")
        for name, agent in self.agents.items():
            if name.startswith("citizen"):
                agent.respond(self.message_pool)

    def _developer_revision(self):
        logging.info("Developer making adjustments based on feedback.")
        self.agents["developer"].respond(self.message_pool, stage="conclusion")

    def _government_decision(self):
        logging.info("Government making decision on the project.")
        self.agents["government"].respond(self.message_pool)

    def _log_conversation(self):
        try:
            self.message_pool.log_conversation(self.output_file)
            logging.info("Conversation logged successfully.")
        except Exception as e:
            logging.error(f"Failed to write conversation log: {e}")
            raise

    def start_flow(self):
        """Initiate the binary flow sequence of interactions."""
        self._developer_intro()
        self._collect_citizen_feedback()
        self._developer_revision()
        self._government_decision()
        self._log_conversation()
        logging.info("Binary flow completed.")
