import os
from langchain_groq import ChatGroq

model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

llm = ChatGroq(
    temperature=0.1,
    model_name=model_name,
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=1500,
    max_retries=5
)