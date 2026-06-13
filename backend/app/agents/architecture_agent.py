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
        # Bind the Pydantic schema natively to the LLM
        self.structured_llm = llm.with_structured_output(ArchitectureReview)

    def run(self, patches: list[str]) -> tuple[ArchitectureReview, dict]:
        # Handle empty patch lists without making an external API call
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
        """

        try:
            # Invoking the structured LLM guarantees an output conforming to ArchitectureReview
            response_obj = self.structured_llm.invoke(prompt)
            
            # Extract token usage metadata safely
            token_usage = {}
            if hasattr(response_obj, "response_metadata"):
                token_usage = response_obj.response_metadata.get("token_usage", {})
                
            return response_obj, token_usage

        except Exception as e:
            print(f"Error in ArchitectureAgent structured invocation: {e}")
            # Fallback securely to prevent crashing the LangGraph compilation thread
            fallback_review = ArchitectureReview(
                is_solid=False,
                strengths=[],
                weaknesses=[f"Failed to execute architecture schema parser: {str(e)}"],
                recommendations=["Rerun webhook worker or execute a manual design evaluation."]
            )
            return fallback_review, {}