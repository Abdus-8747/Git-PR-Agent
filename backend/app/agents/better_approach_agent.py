import json
from pydantic import BaseModel, Field
from app.services.llm_service import llm

class BetterApproachReview(BaseModel):
    has_better_approach: bool = Field(
        ...,
        description="True ONLY if the code inside the patch is actively bad, unoptimized, or fundamentally flawed. False for straightforward, valid fixes."
    )
    current_implementation: str = Field(
        ...,
        description="A brief summary of how the current patch implements the logic."
    )
    suggested_implementation: str = Field(
        ...,
        description="A brief, high-value alternative code implementation or pattern suggestion. Put 'None' if has_better_approach is False."
    )
    reasoning: str = Field(
        ...,
        description="Justification for why this change is necessary (e.g., performance, readability, scale), or why the current patch is sufficient."
    )

class BetterApproachAgent:
    def __init__(self):
        # Native structured validation binding
        self.structured_llm = llm.with_structured_output(BetterApproachReview)

    def run(self, patches: list[str]) -> tuple[BetterApproachReview, dict]:
        # Handle empty patch sets without executing an LLM runtime cycle
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
        """

        try:
            # Structuring guarantees clean serialization matching the Pydantic class map
            response_obj = self.structured_llm.invoke(prompt)
            
            # Extract metrics metadata safely
            token_usage = {}
            if hasattr(response_obj, "response_metadata"):
                token_usage = response_obj.response_metadata.get("token_usage", {})
                
            return response_obj, token_usage

        except Exception as e:
            print(f"Error in BetterApproachAgent structured invocation: {e}")
            # Fail-safe defensive return to allow graph execution continuity
            fallback_review = BetterApproachReview(
                has_better_approach=False,
                current_implementation="Unknown",
                suggested_implementation="None",
                reasoning=f"Automated pipeline fallback triggered by processing exception: {str(e)}"
            )
            return fallback_review, {}