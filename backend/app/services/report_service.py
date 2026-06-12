def build_commit_report(
    repo_name: str,
    author: str,
    commit_message: str,
    analysis: dict,
):
    return f"""
🚀 New Commit Detected

📦 Repo: {repo_name}

👨‍💻 Author: {author}

💬 Commit:
{commit_message}

📂 Category:
{analysis["category"]}

⚡ Impact:
{analysis["impact"]}

📝 Summary:
{analysis["summary"]}
"""