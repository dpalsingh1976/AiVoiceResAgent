
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables.")
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()

async def execute_query(query: str, *args):
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables.")
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.execute(query, *args)
        return result
    except Exception as e:
        print(f"Database query error: {e}")
        raise
    finally:
        if conn:
            await conn.close()

async def fetch_one(query: str, *args):
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables.")
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        record = await conn.fetchrow(query, *args)
        return record
    except Exception as e:
        print(f"Database fetch_one error: {e}")
        raise
    finally:
        if conn:
            await conn.close()

async def fetch_all(query: str, *args):
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables.")
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        records = await conn.fetch(query, *args)
        return records
    except Exception as e:
        print(f"Database fetch_all error: {e}")
        raise
    finally:
        if conn:
            await conn.close()


