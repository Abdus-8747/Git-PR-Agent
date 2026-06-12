# app/agents/developer_agent.py

import json
from pydantic import BaseModel
from app.services.llm_service import llm

class DeveloperAnalysis(BaseModel):
    feature_type: str
    implementation_summary: str
    complexity: str
    files_touched: list[str]
    potential_issues: list[str]

class DeveloperAgent:
    def run(self, commit_message: str, files_changed: list[str], patches: list[str]) -> DeveloperAnalysis:
        prompt = f"""
        You are a pragmatic Senior Developer. Analyze the following commit and changed files.
        CRITICAL RULES:
        1. Provide a concise summary of the changes based on the code diffs.
        2. DO NOT hallucinate "potential issues" (like "potential breaking changes" or "inconsistencies") unless you see glaring evidence of it in the files touched and commit message. Generic warnings must be avoided.
        3. Keep the potential_issues array empty if the commit is just a standard change, refactor, or simple fix.

        Commit Message:
        {commit_message}

        Files Changed:
        {files_changed}
        
        Patches (Code Diffs):
        {patches}

        Return ONLY a valid JSON object matching this schema exactly:
        {{
            "feature_type": "string",
            "implementation_summary": "string",
            "complexity": "Low/Medium/High",
            "files_touched": ["string"],
            "potential_issues": ["string (only if specific and highly likely)"]
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
            
            # Ensure potential_issues is a list
            if "potential_issues" not in data:
                data["potential_issues"] = []
                
            token_usage = getattr(response, "response_metadata", {}).get("token_usage", {})
            return DeveloperAnalysis(**data), token_usage

        except Exception as e:
            print(f"Error in DeveloperAgent: {e}")
            return DeveloperAnalysis(
                feature_type="Unknown",
                implementation_summary="Failed to parse analysis.",
                complexity="Unknown",
                files_touched=files_changed,
                potential_issues=[f"Error: {str(e)}"]
            ), {}