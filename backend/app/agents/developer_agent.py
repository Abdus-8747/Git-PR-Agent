import json
from typing import Literal
from pydantic import BaseModel, Field
from app.services.llm_service import llm

class DeveloperAnalysis(BaseModel):
    feature_type: str = Field(
        ..., 
        description="The category of the change, e.g., Bug Fix, Feature, Refactor, Documentation, CI/CD."
    )
    implementation_summary: str = Field(
        ..., 
        description="A concise, pragmatic summary of what technical changes were actually introduced based on the code diff."
    )
    complexity: Literal["Low", "Medium", "High"] = Field(
        ..., 
        description="The overall code complexity and risk level of the code modifications."
    )
    files_touched: list[str] = Field(
        default_factory=list,
        description="List of file paths that were modified, added, or deleted in this commit."
    )
    potential_issues: list[str] = Field(
        default_factory=list,
        description="Highly specific, glaring issues or bugs visible in the code. Leave empty unless there is concrete evidence."
    )


class DeveloperAgent:
    def __init__(self):
        # FIX: Added include_raw=True to prevent LangChain from dropping response metadata
        self.structured_llm = llm.with_structured_output(DeveloperAnalysis, include_raw=True)

    def run(self, commit_message: str, files_changed: list[str], patches: list[str]) -> tuple[DeveloperAnalysis, dict]:
        prompt = f"""
        You are a pragmatic Senior Developer. Analyze the following commit and changed files.
        
        CRITICAL RULES:
        1. Provide a concise, highly accurate summary of the changes based on the code diffs.
        2. DO NOT hallucinate "potential issues" (like "potential breaking changes" or "inconsistencies") unless you see glaring evidence of it in the files touched and commit message. Generic warnings must be avoided.
        3. Keep the potential_issues array empty if the commit is just a standard change, refactor, or simple fix.

        Commit Message:
        {commit_message}

        Files Changed:
        {files_changed}
        
        Patches (Code Diffs):
        {patches}
        """

        try:
            # When include_raw=True, this returns a dict: {"parsed": PydanticModel, "raw": AIMessage}
            response_payload = self.structured_llm.invoke(prompt)
            
            # Extract the successfully instantiated Pydantic object
            parsed_analysis = response_payload["parsed"]
            
            # Extract the raw message container holding metadata
            raw_message = response_payload["raw"]
            
            # Secure token extraction mapping across primary provider variations (Groq/OpenAI)
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
            
            return parsed_analysis, token_usage

        except Exception as e:
            print(f"Error in DeveloperAgent structured invocation: {e}")
            fallback_analysis = DeveloperAnalysis(
                feature_type="Unknown",
                implementation_summary="Failed to parse analysis due to an internal execution error.",
                complexity="Low",
                files_touched=files_changed,
                potential_issues=[f"Agent Execution Error: {str(e)}"]
            )
            return fallback_analysis, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}