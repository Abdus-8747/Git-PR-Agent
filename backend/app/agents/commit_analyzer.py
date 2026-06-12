from app.services.llm_service import llm
import json

def analyze_commit(message: str):
    prompt = f"""
    Analyze this git commit and return ONLY a valid JSON object.

    Commit:
    {message}

    Format exactly like this:
    {{
        "category": "Feature",
        "impact": "High",
        "summary": "Added JWT authentication and refresh token support"
    }}
    """

    result = llm.invoke(prompt)

    content = result.content.strip()

    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    return json.loads(content)