# app/agents/principal_engineer_agent.py

import json
from pydantic import BaseModel
from app.services.llm_service import llm

class PrincipalReview(BaseModel):
    overall_score: float
    verdict: str
    approval_status: str
    priority_fixes: list[str]

class PrincipalEngineerAgent:
    def run(
        self,
        developer_analysis,
        security_review,
        architecture_review,
        better_approach_review
    ) -> PrincipalReview:
        
        prompt = f"""
        You are a highly pragmatic Principal Staff Engineer. You need to review the aggregated analysis of a recent commit 
        and provide a final verdict.
        
        Developer Analysis: {developer_analysis.model_dump_json() if developer_analysis else 'None'}
        Security Review: {security_review.model_dump_json() if security_review else 'None'}
        Architecture Review: {architecture_review.model_dump_json() if architecture_review else 'None'}
        Better Approach Review: {better_approach_review.model_dump_json() if better_approach_review else 'None'}

        CRITICAL RULES:
        1. Give a high score (9-10) and an "Approved" status unless there is a genuine, undeniable bug, vulnerability, or architectural flaw that will break the application.
        2. DO NOT reject a commit or demand priority fixes just because it lacks enterprise features (like dependency injection) or doesn't fix things outside the scope of the commit.
        3. Only list priority_fixes if they are ABSOLUTELY REQUIRED before merging.
        4. Be encouraging. If the commit is a simple fix or feature, approve it.

        Based on these inputs, give an overall score (0 to 10), a short text verdict, an approval status 
        (Approved, Changes Requested, Rejected), and a list of any critical priority fixes required.

        Return ONLY a valid JSON object matching this schema exactly:
        {{
            "overall_score": float (0-10),
            "verdict": "string",
            "approval_status": "Approved/Changes Requested/Rejected",
            "priority_fixes": ["string (only if absolutely necessary)"]
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
            
            if "priority_fixes" not in data:
                data["priority_fixes"] = []
                
            token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return PrincipalReview(**data), token_usage

        except Exception as e:
            print(f"Error in PrincipalEngineerAgent: {e}")
            return PrincipalReview(
                overall_score=0.0,
                verdict=f"Failed to compile final review: {str(e)}",
                approval_status="Changes Requested",
                priority_fixes=["Investigate agent failure"]
            ), {}