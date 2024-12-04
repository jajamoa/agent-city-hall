# src/simulation/simulate.py
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import json
import concurrent.futures
import numpy as np
from src.utils import LLaMAClient, OpenAIClient
from src.prompts import OPINION_DISTRIBUTION_PROMPT, SUPPORTER_DISTRIBUTION_PROMPT, OPPONENT_DISTRIBUTION_PROMPT, SIMULATED_AGENT_COMMENT_PROMPT

class SimulationEngine:
    def __init__(self):
        self.llama_client = LLaMAClient()
        self.openai_client = OpenAIClient()
        self.reason_dictionary = json.load(open("data/reasons.json"))
        
    def simulate(self, region, population, proposal, demographics):
        # generate distribution of opinions
        opinion_distribution = self._simulate_opinion_distribution(region, population, proposal, demographics)
        
        # generate sample agents (deterministic based on demographics)
        sample_agents = self._generate_sample_agents(demographics)
        
        # generate sample comments for each agent
        sample_agents = self._generate_sample_comments(region, sample_agents, proposal)
        
        return opinion_distribution, sample_agents
        
    def _generate_sample_agents(self, demographics, N=30):
        # generate sample agents based on demographics
        # attributes include age, income, education, occupation, gender, religion, and race.
        def sample_attribute(attr_name, demographics):
            # sample an attribute based on demographics
            dist_data = demographics[attr_name + "_distribution"]
            options = list(dist_data.keys())
            p = list(dist_data.values())
            p = np.array(p) / np.sum(p)
            sampled_value = np.random.choice(options, p=p)
            return sampled_value
        
        attributes = ["age", "income", "education", "occupation", "gender", "religion", "race"]
        sample_agents = {}
        for i in range(N):
            agent = {}
            for attr in attributes:
                agent[attr] = sample_attribute(attr, demographics)
            sample_agents[i] = {"id": i, "agent": agent}
        return sample_agents
    
    
    def _generate_sample_comments(self, region, sample_agents, proposal):
        def generate_opinion_and_comment(agent_id, attributes):
            num_attempts = 0
            while num_attempts < 3:
                try:
                    # generate a comment based on attributes and proposal
                    prompt = SIMULATED_AGENT_COMMENT_PROMPT.format(region=region, attributes=attributes, policy=str(proposal))
                    messages = [{"role": "user", "content": prompt}]
                    response = self.openai_client.chat(messages, temperature=1, force_json=True)
                    response = json.loads(response)
                    opinion = response["opinion"]
                    comment = response["comment"]
                    # print(f"Agent ID: {agent_id}, Opinion: {opinion}, Comment: {comment}")
                    return agent_id, opinion, comment
                except Exception as e:
                    print(f"Retrying for agent {agent_id} due to error: {e}")
                    num_attempts += 1
            print(f"Failed to generate comment for agent {agent_id}")
            return agent_id, None, None
        
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Create a list of futures
            futures = {
                executor.submit(generate_opinion_and_comment, agent_id, agent["agent"]): agent_id
                for agent_id, agent in sample_agents.items()
            }

            # Process completed futures
            for future in concurrent.futures.as_completed(futures):
                agent_id = futures[future]
                try:
                    agent_id, opinion, comment = future.result()
                    if opinion and comment:
                        sample_agents[agent_id]["opinion"] = opinion
                        sample_agents[agent_id]["comment"] = comment
                except Exception as e:
                    print(f"Error processing result for agent {agent_id}: {e}")

        return sample_agents
            
            
    def _simulate_opinion_distribution(self, region, population, proposal, demographics):
        # generate distribution among supporters, opponents, and neutrals
        # Example: 60% supporters, 30% opponents, 10% neutrals
        dist = self._generate_distribution(region, proposal, demographics)
        dist_supporter = self._generate_supporter_distribution(region, proposal, demographics)
        dist_opponent = self._generate_opponent_distribution(region, proposal, demographics)
        
        # write the result in a dictionary and return it
        result = {}
        num_supporters = int(population * dist["support"])
        num_opponents = int(population * dist["oppose"])
        num_neutral = population - (num_supporters + num_opponents)
        result["summary_statistics"] = {
            "support": num_supporters,
            "oppose": num_opponents,
            "neutral": num_neutral
        }
        result["supporter_reasons"] = dist_supporter
        result["opponent_reasons"] = dist_opponent
        return result
    
    def _generate_distribution(self, region, proposal, demographics):
        # generate distribution among supporters, opponents, and neutrals
        # Example: 60% supporters, 30% opponents, 10% neutrals
        prompt = OPINION_DISTRIBUTION_PROMPT.format(region=region, policy=str(proposal), demographics=demographics)
        messages = [{"role": "user", "content": prompt}]
        target_words = ["A", "B", "C"]
        _, probabilities = self.llama_client.get_logits(messages, target_words)
        probabilities = probabilities.cpu().numpy().flatten()
        dist = {"support": float(probabilities[0]), "oppose": float(probabilities[1]), "neutral": float(probabilities[2])}
        assert abs(sum(dist.values()) - 1) < 1e-6, "Distribution must sum to 1"
        return dist
    
    def _generate_supporter_distribution(self, region, proposal, demographics):
        # generate distribution of reasons among supporters
        reasons_list = self.reason_dictionary["support_reasons"]
        reasons = ' '.join([f"{chr(ord('A')+i)}. {reason}" for i, reason in enumerate(reasons_list)])
        prompt = SUPPORTER_DISTRIBUTION_PROMPT.format(region=region, policy=str(proposal), reasons=reasons)
        print(prompt)
        messages = [{"role": "user", "content": prompt}]
        target_words = [chr(ord('A')+i) for i in range(len(reasons_list))]
        _, probabilities = self.llama_client.get_logits(messages, target_words)
        probabilities = probabilities.cpu().numpy().flatten()
        dist = {reason: float(probabilities[i]) for i, reason in enumerate(reasons_list)}
        assert abs(sum(dist.values()) - 1) < 1e-6, "Distribution must sum to 1"
        return dist
        
    def _generate_opponent_distribution(self, region, proposal, demographics):
        # generate distribution of reasons among opponents
        reasons_list = self.reason_dictionary["oppose_reasons"]
        reasons = ' '.join([f"{chr(ord('A')+i)}. {reason}" for i, reason in enumerate(reasons_list)])
        prompt = OPPONENT_DISTRIBUTION_PROMPT.format(region=region, policy=str(proposal), reasons=reasons)
        messages = [{"role": "user", "content": prompt}]
        target_words = [chr(ord('A')+i) for i in range(len(reasons_list))]
        _, probabilities = self.llama_client.get_logits(messages, target_words)
        probabilities = probabilities.cpu().numpy().flatten()
        dist = {reason: float(probabilities[i]) for i, reason in enumerate(reasons_list)}
        assert abs(sum(dist.values()) - 1) < 1e-6, "Distribution must sum to 1"
        return dist