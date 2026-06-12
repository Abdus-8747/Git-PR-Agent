import asyncio
import sys
import os

# Add the project root to the python path so that app modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.db import engine, Base
# Import all models here so that Base.metadata knows about them
from app.database.models import (
    CommitAnalysis,
    DeveloperAnalysisModel,
    OrchestratorDecisionModel,
    SecurityReviewModel,
    ArchitectureReviewModel,
    BetterApproachReviewModel,
    PrincipalReviewModel
)

async def init_models(drop_all: bool = False):
    """
    Initialize the database models.
    If drop_all is True, it will drop all existing tables before recreating them.
    WARNING: drop_all=True will delete all your data!
    """
    async with engine.begin() as conn:
        if drop_all:
            print("Dropping all existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("All tables dropped.")
            
        print("Creating tables based on models...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database schema updated successfully!")

if __name__ == "__main__":
    # Check if the user passed '--drop' as an argument
    should_drop = "--drop" in sys.argv
    
    if should_drop:
        print("WARNING: You are about to drop all tables and lose all data.")
        confirmation = input("Are you sure? (y/n): ")
        if confirmation.lower() != 'y':
            print("Aborting.")
            sys.exit(0)
            
    asyncio.run(init_models(drop_all=should_drop))
