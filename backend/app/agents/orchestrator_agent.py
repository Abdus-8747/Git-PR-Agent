from pydantic import BaseModel
from app.services.llm_service import llm
import json


class OrchestratorDecision(BaseModel):
    run_security_review: bool
    run_architecture_review: bool
    run_better_approach_review: bool
    review_depth: str
    reasoning: str


class OrchestratorAgent:

    def run(
        self,
        commit_message: str,
        files_changed: list[str],
        patches: list[str]
    ) -> OrchestratorDecision:

        prompt = f"""
        You are an experienced Engineering Manager.

        Analyze the commit and decide which reviewers should participate.
        Security Review: True if files involve auth, credentials, crypto, validation, infrastructure, OR if the code changes contain hardcoded passwords, tokens, API keys, or raw SQL queries.
        Architecture Review: True if files involve core patterns, database schemas, API definitions, or heavy refactoring.
        Better Approach Review: True if files involve complex logic, algorithms, or typical code smells.

        Commit Message:
        {commit_message}

        Files Changed:
        {files_changed}
        
        Patches (Code Changes):
        {patches}

        Review Depth Rules:
        - Small changes => normal
        - Medium changes => deep
        - Large refactors => extensive

        Return ONLY a valid JSON object matching this schema exactly:
        {{
            "run_security_review": true/false,
            "run_architecture_review": true/false,
            "run_better_approach_review": true/false,
            "review_depth": "string",
            "reasoning": "string"
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

            token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return OrchestratorDecision(**data), token_usage

        except Exception as e:
            print(f"Error in OrchestratorAgent: {e}")
            return OrchestratorDecision(
                run_security_review=True,
                run_architecture_review=True,
                run_better_approach_review=True,
                review_depth="normal",
                reasoning=f"Fallback decision due to error: {str(e)}",
            ), {}