from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
        raise RuntimeError("DATABASE_URL is not set")

if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql", 1)

if "psycopg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_async_engine(DATABASE_URL)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)