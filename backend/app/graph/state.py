from typing import TypedDict, Annotated, Optional
import operator

# Import our unified structured Pydantic models from their respective agents
from app.agents.developer_agent import DeveloperAnalysis
from app.agents.orchestrator_agent import OrchestratorDecision
from app.agents.security_agent import SecurityReview
from app.agents.architecture_agent import ArchitectureReview
from app.agents.better_approach_agent import BetterApproachReview
from app.agents.principal_engineer_agent import PrincipalReview


class TokenMetric(TypedDict):
    """
    Strictly structures telemetry logs emitted by our foundational models.
    Prevents agents from passing non-standard or breaking log payloads.
    """
    agent: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]


def merge_token_usage(left: list[TokenMetric], right: list[TokenMetric]) -> list[TokenMetric]:
    """
    Defensive reducer tracking agent telemetry logs across execution steps.
    Handles parallel execution threads gracefully without dropping log elements.
    """
    return (left or []) + (right or [])


class AgentState(TypedDict):
    # ==========================================
    # Webhook Payload Inputs
    # ==========================================
    repo_name: str
    commit_sha: str
    commit_message: str
    files_changed: list[str]
    patches: list[str]

    # ==========================================
    # Intermediate Analysis Objects
    # ==========================================
    developer_analysis: Optional[DeveloperAnalysis]
    orchestrator_decision: Optional[OrchestratorDecision]

    # ==========================================
    # Specialized Reviewer Outputs 
    # (Optional because the Orchestrator can bypass them)
    # ==========================================
    security_review: Optional[SecurityReview]
    architecture_review: Optional[ArchitectureReview]
    better_approach_review: Optional[BetterApproachReview]

    # ==========================================
    # Evaluation Verdict & Reporting Targets
    # ==========================================
    principal_review: Optional[PrincipalReview]
    final_summary: Optional[str]
    
    # ==========================================
    # Telemetry and Budget Accumulator
    # ==========================================
    # Fixed from list[dict] with operator.add to prevent flat raw concatenations
    token_usage: Annotated[list[TokenMetric], merge_token_usage]