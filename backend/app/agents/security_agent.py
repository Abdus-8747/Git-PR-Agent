# app/agents/security_agent.py

import json
from pydantic import BaseModel
from app.services.llm_service import llm

class SecurityReview(BaseModel):
    is_secure: bool
    vulnerabilities: list[str]
    recommendations: list[str]
    risk_level: str

class SecurityAgent:
    def run(self, patches: list[str]) -> SecurityReview:
        if not patches:
            return SecurityReview(
                is_secure=True,
                vulnerabilities=[],
                recommendations=[],
                risk_level="None"
            ), {}
            
        prompt = f"""
        You are a pragmatic Senior Security Engineer. Review the following code patches.
        CRITICAL RULES:
        1. ONLY comment on the exact lines of code added or modified in the patches.
        2. DO NOT hallucinate missing features (e.g., "missing authorization" or "no rate limiting") if the patch is just a simple refactor or a small change.
        3. Default to "is_secure: true" and "risk_level: None" UNLESS you see a blatant, undeniable security vulnerability directly introduced in this patch.
        4. Do not flag standard best practices (like reading from environment variables) as potential risks unless the implementation is actively malicious or fundamentally broken.

        Patches:
        {patches}

        Return ONLY a valid JSON object matching this schema exactly:
        {{
            "is_secure": true/false,
            "vulnerabilities": ["string (only if undeniable vulnerability is found)"],
            "recommendations": ["string (only actionable fixes for the patch)"],
            "risk_level": "Low/Medium/High/Critical/None"
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
            if "vulnerabilities" not in data:
                data["vulnerabilities"] = []
            if "recommendations" not in data:
                data["recommendations"] = []
                
            token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return SecurityReview(**data), token_usage

        except Exception as e:
            print(f"Error in SecurityAgent: {e}")
            return SecurityReview(
                is_secure=False,
                vulnerabilities=[f"Failed to parse security analysis: {str(e)}"],
                recommendations=["Manual security review required."],
                risk_level="Unknown"
            ), {}