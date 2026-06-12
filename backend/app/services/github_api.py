import os
import requests
from typing import Tuple, List

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def fetch_commit_details(repo_full_name: str, commit_sha: str) -> Tuple[List[str], List[str]]:
    """
    Fetches the list of files changed and the patches for a specific commit.
    Returns (files_changed, patches)
    """
    if not GITHUB_TOKEN:
        print("Warning: GITHUB_TOKEN not found in environment. Cannot fetch patches.")
        return [], []

    url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        files_changed = []
        patches = []

        for file_data in data.get("files", []):
            filename = file_data.get("filename")
            patch = file_data.get("patch", "")
            
            if filename:
                files_changed.append(filename)
                
            # If the file was changed but has no patch (e.g. binary file or too large), skip the patch
            if patch:
                patches.append(f"File: {filename}\n{patch}")

        return files_changed, patches

    except requests.exceptions.RequestException as e:
        print(f"Error fetching commit details from GitHub API: {e}")
        return [], []
