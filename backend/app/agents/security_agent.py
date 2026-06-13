import json
from typing import Literal
from pydantic import BaseModel, Field
from app.services.llm_service import llm

class SecurityReview(BaseModel):
    is_secure: bool = Field(
        ..., 
        description="True if the code modifications introduce no glaring vulnerabilities. Defaults to True."
    )
    vulnerabilities: list[str] = Field(
        default_factory=list,
        description="List of undeniable security vulnerabilities directly introduced in this patch. Leave empty if none."
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable, highly explicit security fixes targeting only the code lines present in the patch."
    )
    risk_level: Literal["Low", "Medium", "High", "Critical", "None", "Unknown"] = Field(
        ..., 
        description="The maximum severity of security risk directly introduced by these patch changes."
    )


class SecurityAgent:
    def __init__(self):
        # FIX: Added include_raw=True to ensure the raw AIMessage envelope is accessible
        self.structured_llm = llm.with_structured_output(SecurityReview, include_raw=True)

    def run(self, patches: list[str]) -> tuple[SecurityReview, dict]:
        # Short-circuit early if there are no code patches to examine
        if not patches:
            return SecurityReview(
                is_secure=True,
                vulnerabilities=[],
                recommendations=[],
                risk_level="None"
            ), {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            
        prompt = f"""
        You are a pragmatic Senior Security Engineer. Review the following code patches.
        
        CRITICAL RULES:
        1. ONLY comment on the exact lines of code added or modified in the patches.
        2. DO NOT hallucinate missing features (e.g., "missing authorization" or "no rate limiting") if the patch is just a simple refactor or a small change.
        3. Default to "is_secure: true" and "risk_level: None" UNLESS you see a blatant, undeniable security vulnerability directly introduced in this patch.
        4. Do not flag standard best practices (like reading from environment variables) as potential risks unless the implementation is actively malicious or fundamentally broken.

        Patches:
        {patches}
        """

        try:
            # response_payload is a dict mapping keys: "parsed" and "raw"
            response_payload = self.structured_llm.invoke(prompt)
            
            # Extract parsed structural Pydantic model
            parsed_review = response_payload["parsed"]
            
            # Extract raw underlying message context holding metadata logs
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
            print(f"Error in SecurityAgent structured invocation: {e}")
            fallback_review = SecurityReview(
                is_secure=False,
                vulnerabilities=[f"Failed to execute security schema parser: {str(e)}"],
                recommendations=["Rerun webhook execution or perform manual inspection of diff patches."],
                risk_level="Unknown"
            )
            return fallback_review, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}