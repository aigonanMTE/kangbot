import asyncpg
import os
import datetime
import discord

# PostgreSQL 연결
DB_URL = os.getenv("DATABASE_URL")

async def get_conn():
    return await asyncpg.connect(DB_URL)

# 유저 존재 확인
async def check_in_db(user):
    try:
        conn = await get_conn()
        result = await conn.fetchrow("SELECT 1 FROM user_reviews WHERE discord_id = $1", user.id)
        await conn.close()
        return result is not None
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False

# 유저 추가
async def add_user(user):
    try:
        if await check_in_db(user):
            return False
        conn = await get_conn()
        await conn.execute(
            "INSERT INTO user_reviews (discord_id, point, scamer) VALUES ($1, $2, $3)",
            user.id, 350, False
        )
        await conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False

# 포인트 조회
async def get_point(user):
    try:
        conn = await get_conn()
        row = await conn.fetchrow("SELECT point FROM user_reviews WHERE discord_id = $1", user.id)
        await conn.close()
        if row:
            return row['point'] / 10
        return False
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False

# 포인트 변경
async def chainge_point(user, delta):
    try:
        current = await get_point(user)
        if current is False:
            return False
        new_point = int((current + delta) * 10)
        conn = await get_conn()
        await conn.execute(
            "UPDATE user_reviews SET point = $1 WHERE discord_id = $2",
            new_point, user.id
        )
        await conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False

# 후기 시간 기록
async def add_review_time(user):
    try:
        now = datetime.datetime.utcnow()
        conn = await get_conn()
        await conn.execute(
            "UPDATE user_reviews SET last_review_time = $1 WHERE discord_id = $2",
            now, user.id
        )
        await conn.close()
    except Exception as e:
        print(f"PostgreSQL error: {e}")
        return False
    
async def main(good: bool, target_user: discord.Member, user: discord.Member, channel: discord.TextChannel):
    if not await check_in_db(target_user):
        print(f"타겟 유저가 db에 없음: {target_user.name}({target_user.id})")
        await add_user(target_user)
    if not await check_in_db(user):
        print(f"유저가 db에 없음 : {user.name}({user.id})")
        await add_user(user)

    point_change = 5 if good else -5
    await chainge_point(target_user, point_change)
    await channel.send(f"{user.mention}님이 후기를 제출했습니다.")