import html
from datetime import datetime
from typing import Optional

from app.agents.developer_agent import DeveloperAnalysis
from app.agents.security_agent import SecurityReview
from app.agents.architecture_agent import ArchitectureReview
from app.agents.better_approach_agent import BetterApproachReview
from app.agents.principal_engineer_agent import PrincipalReview


class SummaryAgent:
    def run(
        self,
        repo_name: str,
        commit_sha: str,
        commit_message: str,
        developer_analysis: Optional[DeveloperAnalysis],
        security_review: Optional[SecurityReview],
        architecture_review: Optional[ArchitectureReview],
        better_approach_review: Optional[BetterApproachReview],
        principal_review: Optional[PrincipalReview],
    ) -> str:
        
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # 1. Evaluate alert levels defensively checking for bypassed nodes
        alert_emoji = "✅"
        alert_text = "All Good"
        is_high_risk = False
        
        # Safely parse security results if the security node wasn't bypassed
        if security_review:
            risk_level = getattr(security_review, "risk_level", "None")
            is_secure = getattr(security_review, "is_secure", True)
            if risk_level in ["High", "Critical"] or not is_secure:
                is_high_risk = True
                
        # Safely parse principal findings if available
        if principal_review:
            approval_status = getattr(principal_review, "approval_status", "Approved")
            if approval_status != "Approved":
                is_high_risk = True
            
        if is_high_risk:
            alert_emoji = "🚨"
            alert_text = "URGENT ATTENTION REQUIRED"

        # 2. Build the Report Header
        summary = f"{alert_emoji} <b>Git Commit Analysis Report</b> {alert_emoji}\n"
        summary += f"<b>Repository:</b> {html.escape(str(repo_name))}\n"
        summary += f"<b>Commit:</b> <code>{html.escape(str(commit_sha[:7]))}</code>\n"
        summary += f"<b>Time:</b> {time_str}\n"
        summary += f"<b>Message:</b> {html.escape(str(commit_message))}\n"
        summary += f"<b>Status:</b> {alert_text}\n\n"

        # 3. Compile Principal Engineer Verdict
        if principal_review:
            verdict = getattr(principal_review, "verdict", "No verbal verdict compiled.")
            score = getattr(principal_review, "overall_score", 10.0)
            fixes = getattr(principal_review, "priority_fixes", [])
            
            summary += f"<b>Verdict:</b> {html.escape(str(verdict))} (Score: {score}/10)\n"
            if fixes:
                summary += "\n<b>Priority Fixes:</b>\n"
                for fix in fixes:
                    summary += f"• {html.escape(str(fix))}\n"

        # 4. Compile Security Bulletins
        if security_review:
            is_secure = getattr(security_review, "is_secure", True)
            risk_level = getattr(security_review, "risk_level", "None")
            vulns = getattr(security_review, "vulnerabilities", [])
            
            if not is_secure and vulns:
                summary += f"\n🛡️ <b>Security Alert (Risk: {html.escape(str(risk_level))}):</b>\n"
                for vuln in vulns:
                    summary += f"• {html.escape(str(vuln))}\n"

        # 5. Compile Developer Space Issues
        if developer_analysis:
            issues = getattr(developer_analysis, "potential_issues", [])
            if issues:
                summary += "\n⚠️ <b>Developer Concerns:</b>\n"
                for issue in issues:
                    summary += f"• {html.escape(str(issue))}\n"

        # 6. Compile Optimizations and Better Architectural Tracks
        if better_approach_review:
            has_better = getattr(better_approach_review, "has_better_approach", False)
            suggestion = getattr(better_approach_review, "suggested_implementation", "None")
            
            if has_better and suggestion and suggestion != "None":
                summary += f"\n💡 <b>Better Approach Suggested:</b>\n{html.escape(str(suggestion))}\n"

        return summary