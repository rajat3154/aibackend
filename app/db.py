import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise RuntimeError("SUPABASE_DB_URL not set")

async def get_db_pool():
    return await asyncpg.create_pool(
    DATABASE_URL,
    min_size=1,
    max_size=5,
    ssl="require",
    statement_cache_size=0  
)

