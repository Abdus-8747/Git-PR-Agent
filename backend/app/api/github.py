from fastapi import APIRouter, Request, HTTPException, BackgroundTasks

from app.utils.github_security import verify_signature
from app.services.telegram_service import send_message
from app.services.github_api import fetch_commit_details
from app.graph.graph import graph
from app.graph.state import AgentState

router = APIRouter()

import asyncio
from app.database.crud import save_agent_state

async def process_commit_in_background(repo_full_name: str, commit_sha: str, commit_message: str):
    print(f"Processing commit {commit_sha} for {repo_full_name} in background...")
    try:
        # 1. Fetch details
        files_changed, patches = fetch_commit_details(repo_full_name, commit_sha)
        
        # 2. Build initial state
        initial_state: AgentState = {
            "repo_name": repo_full_name,
            "commit_sha": commit_sha,
            "commit_message": commit_message,
            "files_changed": files_changed,
            "patches": patches,
            "developer_analysis": None,
            "orchestrator_decision": None,
            "security_review": None,
            "architecture_review": None,
            "better_approach_review": None,
            "principal_review": None,
            "final_summary": None,
            "token_usage": []
        }
        
        # 3. Invoke graph in a separate thread to avoid blocking the event loop
        result_state = await asyncio.to_thread(graph.invoke, initial_state)
        print("Result state:", result_state)
        
        # 4. Save the final state to the database
        try:
            await save_agent_state(result_state)
            print(f"Successfully saved commit {commit_sha} to database.")
        except Exception as db_e:
            print(f"Failed to save to database: {db_e}")
            
        # 5. Extract final summary and send
        final_summary = result_state.get("final_summary")
        if final_summary:
            send_message(final_summary)
        else:
            print(f"Failed to generate final summary for commit {commit_sha}")
            
    except Exception as e:
        print(f"Error processing commit {commit_sha}: {e}")
        send_message(f"🚨 Error processing commit `{commit_sha[:7]}` in {repo_full_name}: {str(e)}")


@router.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):

    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not verify_signature(body, signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )

    payload = await request.json()
    repo_full_name = payload.get("repository", {}).get("full_name")

    commits = payload.get("commits", [])

    for commit in commits:
        commit_sha = commit.get("id")
        commit_message = commit.get("message")
        
        if commit_sha and commit_message:
            background_tasks.add_task(
                process_commit_in_background,
                repo_full_name,
                commit_sha,
                commit_message
            )

    return {
        "success": True,
        "message": f"Processing {len(commits)} commits in background."
    }