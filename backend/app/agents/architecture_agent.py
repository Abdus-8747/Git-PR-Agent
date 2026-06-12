# app/agents/architecture_agent.py

import json
from pydantic import BaseModel
from app.services.llm_service import llm

class ArchitectureReview(BaseModel):
    is_solid: bool
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]

class ArchitectureAgent:
    def run(self, patches: list[str]) -> ArchitectureReview:
        if not patches:
            return ArchitectureReview(
                is_solid=True,
                strengths=["No code changes to review."],
                weaknesses=[],
                recommendations=[]
            ), {}
            
        prompt = f"""
        You are a pragmatic Software Architect. Review the following code patches.
        CRITICAL RULES:
        1. ONLY comment on the exact lines of code added or modified in the patches.
        2. DO NOT flag missing system-level architecture components (e.g. dependency injection, caching layers) unless the patch fundamentally breaks an existing pattern.
        3. Simple scripts or straightforward functions DO NOT need enterprise-level architecture. Treat them practically.
        4. Default to "is_solid: true" and keep "weaknesses" empty unless there is a severe design flaw (like huge god-functions, hardcoded credentials, or circular dependencies introduced in this patch).

        Patches:
        {patches}

        Return ONLY a valid JSON object matching this schema exactly:
        {{
            "is_solid": true/false,
            "strengths": ["string"],
            "weaknesses": ["string (only severe flaws)"],
            "recommendations": ["string (only actionable fixes for the patch)"]
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
            
            # Ensure lists
            for key in ["strengths", "weaknesses", "recommendations"]:
                if key not in data:
                    data[key] = []
                
            token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return ArchitectureReview(**data), token_usage

        except Exception as e:
            print(f"Error in ArchitectureAgent: {e}")
            return ArchitectureReview(
                is_solid=False,
                strengths=[],
                weaknesses=[f"Failed to parse architecture analysis: {str(e)}"],
                recommendations=["Manual architecture review required."]
            ), {}