from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from app.services.telegram_service import send_message
from app.agents.commit_analyzer import analyze_commit
from app.services.report_service import build_commit_report

from app.api.github import router as github_router
from app.api.data import router as data_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_router)
app.include_router(data_router, prefix="/api")

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/test-telegram")
def test_telegram():
    # Store the True/False result from our updated function
    was_successful = send_message("Hello from FastAPI 🚀")
    
    # Return the actual result
    return {"success": was_successful}

@app.get("/test-report")
def test_report():
    # 1. Get the raw JSON string from the AI
    raw_analysis_string = analyze_commit(
        "feat: add JWT authentication and refresh token support"
    )
    print("Raw AI Output:", raw_analysis_string)  # Debugging line to see the exact output from the LLM
    
    try:
        # 2. Convert the string into a Python dictionary
        analysis_dict = json.loads(raw_analysis_string)
        
        # 3. Pass the dictionary to your builder
        message = build_commit_report(analysis_dict)
        send_message(message)
        
        return analysis_dict
        
    except json.JSONDecodeError:
        print("❌ AI did not return valid JSON!")
        return {"error": "Failed to parse AI output"}

@app.get("/data")
def get_data():
    #import data from neon
    all_data = get_all_commits()
    return all_data