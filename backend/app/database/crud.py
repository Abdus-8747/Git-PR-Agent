from app.database.db import async_session
from app.database.models import (
    CommitAnalysis,
    DeveloperAnalysisModel,
    OrchestratorDecisionModel,
    SecurityReviewModel,
    ArchitectureReviewModel,
    BetterApproachReviewModel,
    PrincipalReviewModel,
    DetectedVulnerability,
    PriorityFix,
    LLMUsageLog
)

async def save_agent_state(state: dict):
    """
    Saves the full LangGraph AgentState to the database.
    """
    async with async_session() as session:
        # Create the main commit record
        commit_analysis = CommitAnalysis(
            repo_name=state.get("repo_name", "unknown"),
            commit_sha=state.get("commit_sha", "unknown"),
            commit_message=state.get("commit_message", ""),
            files_changed=state.get("files_changed", []),
            patches=state.get("patches", []),
            final_summary=state.get("final_summary", "")
        )
        
        # Attach Developer Analysis
        dev_analysis = state.get("developer_analysis")
        if dev_analysis:
            commit_analysis.developer_analysis = DeveloperAnalysisModel(
                feature_type=dev_analysis.feature_type,
                implementation_summary=dev_analysis.implementation_summary,
                complexity=dev_analysis.complexity,
                files_touched=dev_analysis.files_touched,
                potential_issues=dev_analysis.potential_issues
            )
            
        # Attach Orchestrator Decision
        orch_decision = state.get("orchestrator_decision")
        if orch_decision:
            commit_analysis.orchestrator_decision = OrchestratorDecisionModel(
                run_security_review=orch_decision.run_security_review,
                run_architecture_review=orch_decision.run_architecture_review,
                run_better_approach_review=orch_decision.run_better_approach_review,
                review_depth=orch_decision.review_depth,
                reasoning=orch_decision.reasoning
            )
            
        # Attach Security Review and Extract Vulnerabilities
        sec_review = state.get("security_review")
        if sec_review:
            commit_analysis.security_review = SecurityReviewModel(
                is_secure=sec_review.is_secure,
                vulnerabilities=sec_review.vulnerabilities,
                recommendations=sec_review.recommendations,
                risk_level=sec_review.risk_level
            )
            for vuln in sec_review.vulnerabilities:
                vuln_record = DetectedVulnerability(
                    description=vuln,
                    severity=sec_review.risk_level,
                    status="Open"
                )
                commit_analysis.detected_vulnerabilities.append(vuln_record)
            
        # Attach Architecture Review
        arch_review = state.get("architecture_review")
        if arch_review:
            commit_analysis.architecture_review = ArchitectureReviewModel(
                is_solid=arch_review.is_solid,
                strengths=arch_review.strengths,
                weaknesses=arch_review.weaknesses,
                recommendations=arch_review.recommendations
            )
            
        # Attach Better Approach Review
        better_approach = state.get("better_approach_review")
        if better_approach:
            commit_analysis.better_approach_review = BetterApproachReviewModel(
                has_better_approach=better_approach.has_better_approach,
                current_implementation=better_approach.current_implementation,
                suggested_implementation=better_approach.suggested_implementation,
                reasoning=better_approach.reasoning
            )
            
        # Attach Principal Review and Extract Priority Fixes
        principal = state.get("principal_review")
        if principal:
            commit_analysis.principal_review = PrincipalReviewModel(
                overall_score=principal.overall_score,
                verdict=principal.verdict,
                approval_status=principal.approval_status,
                priority_fixes=principal.priority_fixes
            )
            for fix in principal.priority_fixes:
                fix_record = PriorityFix(
                    description=fix,
                    status="Pending"
                )
                commit_analysis.priority_fixes.append(fix_record)

        # Attach LLM Usage Logs
        token_usage_list = state.get("token_usage", [])
        for usage in token_usage_list:
            p_tokens = usage.get("prompt_tokens", 0)
            c_tokens = usage.get("completion_tokens", 0)
            
            # Pricing for llama-3.3-70b-versatile
            # Prompt: $0.59 per 1M tokens
            # Completion: $0.79 per 1M tokens
            calculated_cost = (p_tokens / 1_000_000) * 0.59 + (c_tokens / 1_000_000) * 0.79

            usage_log = LLMUsageLog(
                agent_name=usage.get("agent", "unknown"),
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_cost=usage.get("total_cost", calculated_cost)
            )
            commit_analysis.llm_usage_logs.append(usage_log)

        session.add(commit_analysis)
        await session.commit()
        return commit_analysis
