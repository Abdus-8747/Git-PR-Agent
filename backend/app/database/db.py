import os
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Get the database URL from the environment
raw_db_url = os.getenv("DATABASE_URL")

if not raw_db_url:
    raise ValueError("DATABASE_URL is not set in the environment.")

# Remove surrounding quotes if they exist
raw_db_url = raw_db_url.strip("'\"")

# Convert postgresql:// to postgresql+asyncpg:// for async driver
if raw_db_url.startswith("postgresql://"):
    db_url = raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    db_url = raw_db_url

# asyncpg doesn't support the channel_binding=require or sslmode query parameters directly
db_url = re.sub(r'[?&]channel_binding=require', '', db_url)
db_url = re.sub(r'[?&]sslmode=require', '', db_url)

# If the URL ends with a trailing '?' after stripping parameters, remove it
if db_url.endswith('?'):
    db_url = db_url[:-1]

# Create the async engine
engine = create_async_engine(
    db_url,
    echo=False, # Set to False in production
    connect_args={"ssl": "require"}
)

# Create the session maker
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency for FastAPI
async def get_db():
    async with async_session() as session:
        yield session
