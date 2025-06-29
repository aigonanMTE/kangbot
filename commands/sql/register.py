import discord
import asyncpg
import os

DB_URL = os.getenv("DATABASE_URL")

async def get_conn():
    return await asyncpg.connect(DB_URL)

# 등록 여부 확인
async def check_registered(user: discord.Member):
    try:
        conn = await get_conn()
        result = await conn.fetchrow("SELECT * FROM registered_users WHERE discord_id = $1", user.id)
        await conn.close()

        print(f"Checking registration for user {user.id}: {'Found' if result else 'Not Found'}")
        return result is not None
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False

# 유저 추가
async def add_user(user: discord.Member):
    try:
        if await check_registered(user):
            return False  # 이미 존재

        conn = await get_conn()
        await conn.execute("INSERT INTO registered_users (discord_id) VALUES ($1)", user.id)
        await conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False
