import discord
import sqlite3
import os
from discord.ext import commands

# DB 경로 설정
db_path = os.getenv("DATABASE_PATH")

# DB에 유저 존재 여부 확인
async def check_in_db(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_reviews WHERE discord_id = ?", (user.id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

# 유저 추가
async def add_user(user: discord.Member):
    try:
        if await check_in_db(user):
            return False
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_reviews (discord_id, point, scamer) VALUES (?, ?, ?)", (user.id, 350, False))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

# 포인트 조회 (10으로 나눠서 보여줌)
async def get_point(user: discord.Member):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT point FROM user_reviews WHERE discord_id = ?", (user.id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        point = result[0] / 10
        print(f"포인트 조회 성공: {user.name} {point}")
        return point
    else:
        return False

# 포인트 변경 (표기값 단위로 받아서 DB에는 10배로 저장)
async def chainge_point(user: discord.Member, delta: int):
    try:
        get_point_value = await get_point(user)
        if get_point_value is False:
            print("포인트 조회 실패")
            return False
        new_point = int((get_point_value + delta) * 10)
        print(f"새로운 포인트: {new_point}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE user_reviews SET point = ? WHERE discord_id = ?", (new_point, user.id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

# 전체 흐름 제어 함수
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
