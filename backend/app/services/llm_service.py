import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

class MockResponse:
    def __init__(self, content):
        self.content = content

class SimpleLLM:
    def invoke(self, prompt: str):
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name,
            temperature=0.1,
        )
        return MockResponse(response.choices[0].message.content)

llm = SimpleLLM()