# graph/state.py

from typing import TypedDict, Annotated
import operator

from app.agents.developer_agent import (
    DeveloperAnalysis
)

from app.agents.orchestrator_agent import (
    OrchestratorDecision
)

from app.agents.security_agent import (
    SecurityReview
)

from app.agents.architecture_agent import (
    ArchitectureReview
)

from app.agents.better_approach_agent import (
    BetterApproachReview
)

from app.agents.principal_engineer_agent import (
    PrincipalReview
)


class AgentState(TypedDict):

    repo_name: str
    commit_sha: str
    commit_message: str

    files_changed: list[str]

    patches: list[str]

    developer_analysis: DeveloperAnalysis | None

    orchestrator_decision: OrchestratorDecision | None

    security_review: SecurityReview | None

    architecture_review: ArchitectureReview | None

    better_approach_review: BetterApproachReview | None

    principal_review: PrincipalReview | None

    final_summary: str | None
    
    token_usage: Annotated[list[dict], operator.add]