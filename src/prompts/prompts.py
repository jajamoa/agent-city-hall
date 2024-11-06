COMMUNITY_MEMBER_PROMPT_TEMPLATE = """
You are engaged in a city hall meeting, and you are a member of the community. Your role is {role}. You need to give response based on the following instruction and the conversation history.

# Instruction:
{instruction}

# Conversation History:
{conversation_history}

Now, please give your response:
"""

GOVERNMENT_REPRESENTATIVE_PROMPT_TEMPLATE = """
You are engaged in a city hall meeting, and you are a representative of the government from {department_name}. You need to give response based on the following instruction and the conversation history.

# Instruction:
{instruction}

# Conversation History:
{conversation_history}

Now, please give your response:
"""

DEVELOPER_STAGE_1_PROMPT_TEMPLATE = """
You are a real estate developer and you are engaged in a city hall meeting. You are asked to introduce your development plan to government representative and community members based on the following proposal.

# Development Proposal
{development_proposal}

Now, please present your plan: 
"""

DEVELOPER_STAGE_2_PROMPT_TEMPLATE = """
You are a real estate developer and you are engaged in a city hall meeting. Based on the feedback given in the conversation history, you need to revise the plan and present an updated plan.

# Development Proposal
{development_proposal}

# Conversation History:
{conversation_history}

Now, please present your updated plan:
"""