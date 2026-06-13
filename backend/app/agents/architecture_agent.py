import json
from pydantic import BaseModel, Field
from app.services.llm_service import llm

class ArchitectureReview(BaseModel):
    is_solid: bool = Field(
        ...,
        description="True if the patch maintains robust design patterns, avoids anti-patterns, and handles dependencies correctly. Defaults to True."
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="Concrete, positive architectural choices observed directly within the code patch lines."
    )
    weaknesses: list[str] = Field(
        default_factory=list,
        description="Severe architectural or design flaws (e.g., massive god-functions, tight coupling, circular imports) introduced by this patch."
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Highly actionable architectural fixes targeting structural improvements exclusively for code within the patch."
    )


class ArchitectureAgent:
    def __init__(self):
        # FIX: Added include_raw=True to preserve token metrics in response metadata
        self.structured_llm = llm.with_structured_output(ArchitectureReview, include_raw=True)

    def run(self, patches: list[str]) -> tuple[ArchitectureReview, dict]:
        # Handle empty patch lists without making an external API call
        if not patches:
            return ArchitectureReview(
                is_solid=True,
                strengths=["No code changes to review."],
                weaknesses=[],
                recommendations=[]
            ), {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            
        prompt = f"""
        You are a pragmatic Software Architect. Review the following code patches.
        
        CRITICAL RULES:
        1. ONLY comment on the exact lines of code added or modified in the patches.
        2. DO NOT flag missing system-level architecture components (e.g. dependency injection, caching layers) unless the patch fundamentally breaks an existing pattern.
        3. Simple scripts or straightforward functions DO NOT need enterprise-level architecture. Treat them practically.
        4. Default to "is_solid: true" and keep "weaknesses" empty unless there is a severe design flaw (like huge god-functions, hardcoded credentials, or circular dependencies introduced in this patch).

        Patches:
        {patches}
        """

        try:
            # Invoking with include_raw=True guarantees extraction payload maps to a dictionary
            response_payload = self.structured_llm.invoke(prompt)
            
            # Extract parsed structural Pydantic model
            parsed_review = response_payload["parsed"]
            
            # Extract raw underlying message instance holding tracking parameters
            raw_message = response_payload["raw"]
            
            # Defensive token dictionary tracking logs constructor
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
            print(f"Error in ArchitectureAgent structured invocation: {e}")
            fallback_review = ArchitectureReview(
                is_solid=False,
                strengths=[],
                weaknesses=[f"Failed to execute architecture schema parser: {str(e)}"],
                recommendations=["Rerun webhook worker or execute a manual design evaluation."]
            )
            return fallback_review, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}