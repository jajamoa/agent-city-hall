OPINION_DISTRIBUTION_PROMPT = """
Based on the following housing & development policy and the following demographics of the region, based on your knowledge, how do you think people will respond to the policy?

Region: {region}
Policy: {policy}
Demographics: {demographics}

Please infer how people will respond to the policy: A. Support B. Oppose C. Neutral.
Please enter your choice with the letter only.
"""

SUPPORTER_DISTRIBUTION_PROMPT = """
For the give housing & development policy, among the following 6 categories of reasons, based on your knowledge, what do you think is the biggest reason for the supporters to support this policy?

Region: {region}
Policy: {policy}

Please infer why people would support this policy: {reasons}.
Please enter your choice with the letter only.
"""


OPPONENT_DISTRIBUTION_PROMPT = """
For the given housing & development policy, among the following 6 categories of reasons, based on your knowledge, what do you think is the biggest reason for the opponents to oppose this policy?

Region: {region}
Policy: {policy}

Please infer why people would oppose this policy: {reasons}.
Please enter your choice with the letter only.
"""

SIMULATED_AGENT_COMMENT_PROMPT = """
You are a resident of {region} and you have been asked to comment on the following housing & development policy. 
Your demographic profile is {attributes}.
The policy is as follows: {policy}

First of all, what is your opinion on the policy? Choose one from Support, Oppose, and Neutral. It's open-ended, so feel free to express your opinion.
Then, try to provide a comment that is insightful. Try to keep your comment between 30-80 words.
Please provide your response below in JSON format:
{{
    "opinion": "Support or Oppose or Neutral",
    "comment": "Your comment here."
}}
Now enter the response, make sure it's in JSON format:
"""