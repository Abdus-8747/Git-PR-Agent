from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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