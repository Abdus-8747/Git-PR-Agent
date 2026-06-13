import json
from typing import Literal
from pydantic import BaseModel, Field
from app.services.llm_service import llm


class OrchestratorDecision(BaseModel):
    run_security_review: bool = Field(
        ..., 
        description="True if changes touch auth, tokens, database credentials, raw crypto, sensitive env variables, or custom validation patterns."
    )
    run_architecture_review: bool = Field(
        ..., 
        description="True if changes modify structural setup, database schema migrations, internal API endpoints, hooks, or widespread components."
    )
    run_better_approach_review: bool = Field(
        ..., 
        description="True if changes introduce complex business logic, performance bottlenecks, utility functions, or obvious code smell violations."
    )
    review_depth: Literal["normal", "deep", "extensive"] = Field(
        ..., 
        description="The analysis thoroughness based on code change sizing: small -> normal, medium -> deep, massive/breaking refactors -> extensive."
    )
    reasoning: str = Field(
        ..., 
        description="A concise architectural justification detailing why specific specialist paths were either activated or bypassed."
    )


class OrchestratorAgent:
    def __init__(self):
        # FIX: Added include_raw=True to capture token_usage metadata envelope
        self.structured_llm = llm.with_structured_output(OrchestratorDecision, include_raw=True)

    def run(
        self,
        commit_message: str,
        files_changed: list[str],
        patches: list[str]
    ) -> tuple[OrchestratorDecision, dict]:

        prompt = f"""
        You are an experienced Engineering Manager routing incoming patch streams to specialized reviewer tracks.

        Analyze the commit and decide which specialized engineering reviewers should participate.
        
        Triggering Logic Guidelines:
        - Security Review: True if files involve auth, credentials, crypto, validation, infrastructure, OR if the code changes contain hardcoded passwords, tokens, API keys, or raw SQL queries.
        - Architecture Review: True if files involve core patterns, database schemas, API definitions, or heavy refactoring.
        - Better Approach Review: True if files involve complex logic, algorithms, or typical code smells.

        Commit Message:
        {commit_message}

        Files Changed:
        {files_changed}
        
        Patches (Code Changes):
        {patches}
        """

        try:
            # Unwraps the full response payload dictionary
            response_payload = self.structured_llm.invoke(prompt)
            
            # Extract parsed model object
            parsed_decision = response_payload["parsed"]
            
            # Extract underlying message trace
            raw_message = response_payload["raw"]
            
            # Defensive token dictionary extractor
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
                
            return parsed_decision, token_usage

        except Exception as e:
            print(f"Error in OrchestratorAgent structured invocation: {e}")
            fallback_decision = OrchestratorDecision(
                run_security_review=True,
                run_architecture_review=True,
                run_better_approach_review=True,
                review_depth="normal",
                reasoning=f"Automated defensive routing fallback triggered due to exception: {str(e)}"
            )
            return fallback_decision, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}