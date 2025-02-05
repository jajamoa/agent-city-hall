import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIClient:
    def __init__(self):
        load_dotenv(override=True)
        openai_key = os.getenv('OPENAI_API_KEY')
        print(openai_key)
        if not openai_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        self.client = OpenAI(api_key=openai_key)


    def chat(self, messages, model="gpt-4o-mini", temperature=1, force_json=False):
        try: 
            if force_json:
                response = self.client.chat.completions.create(
                    model=model,
                    response_format={"type": "json_object"},
                    temperature=temperature,
                    messages=messages
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    temperature=temperature,
                    messages=messages
                )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error: {str(e)}"
        
