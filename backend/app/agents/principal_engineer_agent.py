import json
from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.services.llm_service import llm

# Downstream models imported for type hints
from app.agents.developer_agent import DeveloperAnalysis
from app.agents.security_agent import SecurityReview
from app.agents.architecture_agent import ArchitectureReview
from app.agents.better_approach_agent import BetterApproachReview


class PrincipalReview(BaseModel):
    overall_score: float = Field(
        ...,
        description="A technical score between 0.0 and 10.0 representing code health and safety."
    )
    verdict: str = Field(
        ...,
        description="A clear, pragmatic summary explaining the high-level technical assessment of the commit."
    )
    approval_status: Literal["Approved", "Changes Requested", "Rejected"] = Field(
        ...,
        description="The ultimate merge determination based strictly on critical logic soundness."
    )
    priority_fixes: list[str] = Field(
        default_factory=list,
        description="Mandatory fixes that MUST be resolved prior to merging. Leave empty unless there are undeniable app-breaking flaws."
    )


class PrincipalEngineerAgent:
    def __init__(self):
        # FIX: Added include_raw=True to capture token metrics from response envelope
        self.structured_llm = llm.with_structured_output(PrincipalReview, include_raw=True)

    def run(
        self,
        developer_analysis: Optional[DeveloperAnalysis],
        security_review: Optional[SecurityReview],
        architecture_review: Optional[ArchitectureReview],
        better_approach_review: Optional[BetterApproachReview]
    ) -> tuple[PrincipalReview, dict]:
        
        # Defensive string generation checking for bypassed reviewer nodes
        dev_json = developer_analysis.model_dump_json() if developer_analysis else 'None'
        security_json = security_review.model_dump_json() if security_review else 'None'
        arch_json = architecture_review.model_dump_json() if architecture_review else 'None'
        approach_json = better_approach_review.model_dump_json() if better_approach_review else 'None'

        prompt = f"""
        You are a highly pragmatic Principal Staff Engineer. You need to review the aggregated analysis of a recent commit 
        and provide a final verdict.
        
        Developer Analysis: {dev_json}
        Security Review: {security_json}
        Architecture Review: {arch_json}
        Better Approach Review: {approach_json}

        CRITICAL RULES:
        1. Give a high score (9-10) and an "Approved" status unless there is a genuine, undeniable bug, vulnerability, or architectural flaw that will break the application.
        2. DO NOT reject a commit or demand priority fixes just because it lacks enterprise features (like dependency injection) or doesn't fix things outside the scope of the commit.
        3. Only list priority_fixes if they are ABSOLUTELY REQUIRED before merging.
        4. Be encouraging. If the commit is a simple fix or feature, approve it.

        Based on these inputs, give an overall score (0 to 10), a short text verdict, an approval status 
        (Approved, Changes Requested, Rejected), and a list of any critical priority fixes required.
        """

        try:
            # Invoking with include_raw=True returns a wrapper dict: {"parsed": ..., "raw": ...}
            response_payload = self.structured_llm.invoke(prompt)
            
            # Extract parsed structural Pydantic model
            parsed_review = response_payload["parsed"]
            
            # Extract raw underlying message context holding tracking metadata parameters
            raw_message = response_payload["raw"]
            
            # Defensive token metadata dictionary extractor
            token_usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
            
            if hasattr(raw_message, "response_metadata") and raw_message.response_metadata:
                raw_tokens = raw_message.response_metadata.get("token_usage", {})
                
                token_usage["prompt_tokens"] = raw_tokens.get("prompt_tokens") or raw_tokens.get("input_tokens") or 0
                token_usage["completion_tokens"] = raw_tokens.get("completion_tokens") or raw_tokens.get("output_tokens") or 0
                token_usage["total_tokens"] = raw_tokens.get("total_tokens") or (token_usage["prompt_tokens"] + token_usage["completion_tokens"])
                
            return parsed_review, token_usage

        except Exception as e:
            print(f"Error in PrincipalEngineerAgent structured invocation: {e}")
            fallback_review = PrincipalReview(
                overall_score=0.0,
                verdict=f"Principal evaluation layer caught an unhandled generation exception: {str(e)}",
                approval_status="Changes Requested",
                priority_fixes=["Investigate internal agent orchestration failures and parsing logs."]
            )
            return fallback_review, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}