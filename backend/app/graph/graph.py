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
    # Map raw token metrics cleanly to TokenMetric schema wrapper
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
    # Node only executes if explicitly routed here by conditional routing
    result, usage = security_agent.run(patches=state["patches"])
    usage["agent"] = "security"
    return {
        "security_review": result,
        "token_usage": [usage]
    }


def architecture_node(state: AgentState):
    result, usage = architecture_agent.run(patches=state["patches"])
    usage["agent"] = "architecture"
    return {
        "architecture_review": result,
        "token_usage": [usage]
    }


def better_approach_node(state: AgentState):
    result, usage = better_approach_agent.run(patches=state["patches"])
    usage["agent"] = "better_approach"
    return {
        "better_approach_review": result,
        "token_usage": [usage]
    }


def principal_engineer_node(state: AgentState):
    # Uses .get() safely because some preceding reviewer states can be None if bypassed
    result, usage = principal_engineer_agent.run(
        developer_analysis=state.get("developer_analysis"),
        security_review=state.get("security_review"),
        architecture_review=state.get("architecture_review"),
        better_approach_review=state.get("better_approach_review"),
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
        developer_analysis=state.get("developer_analysis"),
        security_review=state.get("security_review"),
        architecture_review=state.get("architecture_review"),
        better_approach_review=state.get("better_approach_review"),
        principal_review=state.get("principal_review"),
    )
    return {
        "final_summary": result
    }

# ==================================================
# Conditional Routing Logic
# ==================================================

def route_to_specialists(state: AgentState) -> list[str]:
    """
    Evaluates the Orchestrator's Pydantic output block dynamically.
    Returns an immediate list of targets to fire in parallel.
    """
    decision = state.get("orchestrator_decision")
    if not decision:
        # Emergency pipeline rescue fallback: go straight to final reviewer
        return ["principal_engineer"]

    destinations = []
    if decision.run_security_review:
        destinations.append("security")
    if decision.run_architecture_review:
        destinations.append("architecture")
    if decision.run_better_approach_review:
        destinations.append("better_approach")

    # If the commit is trivial and orchestrator opts out of all reviews, bypass immediately
    if not destinations:
        return ["principal_engineer"]

    return destinations

# ==================================================
# Graph Architecture Setup
# ==================================================

builder = StateGraph(AgentState)

# Append Worker Processing Entities
builder.add_node("developer", developer_node)
builder.add_node("orchestrator", orchestrator_node)
builder.add_node("security", security_node)
builder.add_node("architecture", architecture_node)
builder.add_node("better_approach", better_approach_node)
builder.add_node("principal_engineer", principal_engineer_node)
builder.add_node("summary", summary_node)

# Linear Edge Foundations
builder.add_edge(START, "developer")
builder.add_edge("developer", "orchestrator")

# Dynamic Fan-Out Conditional Router
builder.add_conditional_edges(
    "orchestrator",
    route_to_specialists,
    {
        "security": "security",
        "architecture": "architecture",
        "better_approach": "better_approach",
        "principal_engineer": "principal_engineer"
    }
)

# Parallel Fan-In Sync Boundaries pointing down to Principal
builder.add_edge("security", "principal_engineer")
builder.add_edge("architecture", "principal_engineer")
builder.add_edge("better_approach", "principal_engineer")

# Final Cleanup Edges
builder.add_edge("principal_engineer", "summary")
builder.add_edge("summary", END)

graph = builder.compile()