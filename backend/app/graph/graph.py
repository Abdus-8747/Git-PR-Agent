# app/graph/graph.py

from langgraph.graph import StateGraph, START, END

from app.graph.state import AgentState

from app.agents.developer_agent import DeveloperAgent
from app.agents.orchestrator_agent import OrchestratorAgent

from app.agents.security_agent import SecurityAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.better_approach_agent import BetterApproachAgent

from app.agents.principal_engineer_agent import PrincipalEngineerAgent
from app.agents.summary_agent import SummaryAgent


# ==================================================
# Agent Instances
# ==================================================

developer_agent = DeveloperAgent()

orchestrator_agent = OrchestratorAgent()

security_agent = SecurityAgent()
architecture_agent = ArchitectureAgent()
better_approach_agent = BetterApproachAgent()

principal_engineer_agent = PrincipalEngineerAgent()

summary_agent = SummaryAgent()


# ==================================================
# Nodes
# ==================================================

def developer_node(state: AgentState):

    result, usage = developer_agent.run(
        commit_message=state["commit_message"],
        files_changed=state["files_changed"],
        patches=state["patches"],
    )

    usage["agent"] = "developer"
    return {
        "developer_analysis": result,
        "token_usage": [usage]
    }


def orchestrator_node(state: AgentState):

    result, usage = orchestrator_agent.run(
        commit_message=state["commit_message"],
        files_changed=state["files_changed"],
        patches=state["patches"]
    )

    usage["agent"] = "orchestrator"
    return {
        "orchestrator_decision": result,
        "token_usage": [usage]
    }


def security_node(state: AgentState):
    decision = state.get("orchestrator_decision")
    if not decision or not decision.run_security_review:
        return {"security_review": None}

    result, usage = security_agent.run(
        patches=state["patches"]
    )
    usage["agent"] = "security"
    return {
        "security_review": result,
        "token_usage": [usage]
    }


def architecture_node(state: AgentState):
    decision = state.get("orchestrator_decision")
    if not decision or not decision.run_architecture_review:
        return {"architecture_review": None}

    result, usage = architecture_agent.run(
        patches=state["patches"]
    )
    usage["agent"] = "architecture"
    return {
        "architecture_review": result,
        "token_usage": [usage]
    }


def better_approach_node(state: AgentState):
    decision = state.get("orchestrator_decision")
    if not decision or not decision.run_better_approach_review:
        return {"better_approach_review": None}

    result, usage = better_approach_agent.run(
        patches=state["patches"]
    )
    usage["agent"] = "better_approach"
    return {
        "better_approach_review": result,
        "token_usage": [usage]
    }


def principal_engineer_node(state: AgentState):

    result, usage = principal_engineer_agent.run(
        developer_analysis=state["developer_analysis"],
        security_review=state["security_review"],
        architecture_review=state["architecture_review"],
        better_approach_review=state["better_approach_review"],
    )

    usage["agent"] = "principal_engineer"
    return {
        "principal_review": result,
        "token_usage": [usage]
    }


def summary_node(state: AgentState):

    result = summary_agent.run(
        repo_name=state["repo_name"],
        commit_sha=state["commit_sha"],
        commit_message=state["commit_message"],
        developer_analysis=state["developer_analysis"],
        security_review=state["security_review"],
        architecture_review=state["architecture_review"],
        better_approach_review=state["better_approach_review"],
        principal_review=state["principal_review"],
    )

    return {
        "final_summary": result
    }


# ==================================================
# Graph
# ==================================================

builder = StateGraph(AgentState)

builder.add_node("developer", developer_node)

builder.add_node("orchestrator", orchestrator_node)

builder.add_node("security", security_node)
builder.add_node("architecture", architecture_node)
builder.add_node("better_approach", better_approach_node)

builder.add_node(
    "principal_engineer",
    principal_engineer_node
)

builder.add_node("summary", summary_node)


# ==================================================
# Edges
# ==================================================

builder.add_edge(
    START,
    "developer"
)

builder.add_edge(
    "developer",
    "orchestrator"
)

builder.add_edge(
    "orchestrator",
    "security"
)

builder.add_edge(
    "orchestrator",
    "architecture"
)

builder.add_edge(
    "orchestrator",
    "better_approach"
)

builder.add_edge(
    "security",
    "principal_engineer"
)

builder.add_edge(
    "architecture",
    "principal_engineer"
)

builder.add_edge(
    "better_approach",
    "principal_engineer"
)

builder.add_edge(
    "principal_engineer",
    "summary"
)

builder.add_edge(
    "summary",
    END
)


graph = builder.compile()