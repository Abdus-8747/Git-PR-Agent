# app/agents/better_approach_agent.py

import json
from pydantic import BaseModel
from app.services.llm_service import llm

class BetterApproachReview(BaseModel):
    has_better_approach: bool
    current_implementation: str
    suggested_implementation: str
    reasoning: str

class BetterApproachAgent:
    def run(self, patches: list[str]) -> BetterApproachReview:
        if not patches:
            return BetterApproachReview(
                has_better_approach=False,
                current_implementation="None",
                suggested_implementation="None",
                reasoning="No patches provided to review."
            ), {}
            
        prompt = f"""
        You are an elite, practical Senior Developer reviewing code patches. 
        CRITICAL RULES:
        1. Only suggest a better approach if the current code in the patch is actively bad, highly unoptimized, or fundamentally flawed.
        2. DO NOT nitpick or suggest complex design patterns for simple scripts.
        3. If the patch is a straightforward bugfix or simple logic, default to "has_better_approach: false".
        4. Focus ONLY on the code that was changed. Do not complain about the surrounding file context that wasn't modified.

        Patches:
        {patches}

        Return ONLY a valid JSON object matching this schema exactly:
        {{
            "has_better_approach": true/false,
            "current_implementation": "string (brief summary)",
            "suggested_implementation": "string (brief suggestion or 'None')",
            "reasoning": "string"
        }}
        """

        try:
            response = llm.invoke(prompt)
            content = response.content.strip()

            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()
            data = json.loads(content)
            
            token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return BetterApproachReview(**data), token_usage

        except Exception as e:
            print(f"Error in BetterApproachAgent: {e}")
            return BetterApproachReview(
                has_better_approach=False,
                current_implementation="Unknown",
                suggested_implementation="Unknown",
                reasoning=f"Failed to parse better approach analysis: {str(e)}"
            ), {}