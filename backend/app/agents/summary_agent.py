# app/agents/summary_agent.py

import html
from datetime import datetime

class SummaryAgent:
    def run(
        self,
        repo_name: str,
        commit_sha: str,
        commit_message: str,
        developer_analysis,
        security_review,
        architecture_review,
        better_approach_review,
        principal_review,
    ) -> str:
        
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Determine if there is a high-level issue
        alert_emoji = "✅"
        alert_text = "All Good"
        
        is_high_risk = False
        if security_review and (security_review.risk_level in ["High", "Critical"] or not security_review.is_secure):
            is_high_risk = True
        if principal_review and principal_review.approval_status != "Approved":
            is_high_risk = True
            
        if is_high_risk:
            alert_emoji = "🚨"
            alert_text = "URGENT ATTENTION REQUIRED"

        summary = f"{alert_emoji} <b>Git Commit Analysis Report</b> {alert_emoji}\n"
        summary += f"<b>Repository:</b> {html.escape(repo_name)}\n"
        summary += f"<b>Commit:</b> <code>{html.escape(commit_sha[:7])}</code>\n"
        summary += f"<b>Time:</b> {time_str}\n"
        summary += f"<b>Message:</b> {html.escape(commit_message)}\n"
        summary += f"<b>Status:</b> {alert_text}\n\n"

        if principal_review:
            summary += f"<b>Verdict:</b> {html.escape(principal_review.verdict)} (Score: {principal_review.overall_score}/10)\n"
            if principal_review.priority_fixes:
                summary += "\n<b>Priority Fixes:</b>\n"
                for fix in principal_review.priority_fixes:
                    summary += f"• {html.escape(fix)}\n"

        if security_review and not security_review.is_secure:
            summary += f"\n🛡️ <b>Security Alert (Risk: {html.escape(security_review.risk_level)}):</b>\n"
            for vuln in security_review.vulnerabilities:
                summary += f"• {html.escape(vuln)}\n"

        if developer_analysis and developer_analysis.potential_issues:
            summary += "\n⚠️ <b>Developer Concerns:</b>\n"
            for issue in developer_analysis.potential_issues:
                summary += f"• {html.escape(issue)}\n"

        if better_approach_review and better_approach_review.has_better_approach:
            summary += f"\n💡 <b>Better Approach Suggested:</b>\n{html.escape(better_approach_review.suggested_implementation)}\n"

        return summary