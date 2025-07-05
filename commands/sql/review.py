import discord
import sqlite3
import os
from discord.ext import commands
import datetime
import logging

# DB 경로 설정
db_path = os.getenv("DATABASE_PATH")
log_db_path = os.getenv("LOG_DATABASE_PATH")

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
        cursor.execute("INSERT INTO user_reviews (discord_id, point, scamer) VALUES (?, ?, ?)", (user.id, 35.0, False))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False

# 포인트 조회 (소수로 바로 반환)
async def get_point(user: discord.Member):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT point FROM user_reviews WHERE discord_id = ?", (user.id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        point = result[0]
        print(f"포인트 조회 성공: {user.name} {point}")
        return point
    else:
        return False

# 포인트 변경 (소수 단위로 받아서 그대로 처리)
async def chainge_point(user: discord.Member, delta: float):
    try:
        current_point = await get_point(user)
        if current_point is False:
            print("포인트 조회 실패")
            return False
        new_point = current_point + delta
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
    

# insert into review_logs (time , target_user, target_user_name, user, user_name, context, Before_point , aefter_point) values (? ,? ,? ,? ,? ,? ,? ,?);
async def add_log(user: discord.Member, target_user: discord.Member, good: bool, ):
    try:
        conn = sqlite3.connect(log_db_path)
        cursor = conn.cursor()
        before_point = await get_point(target_user)
        point_change = 0.5 if good else -0.5
        after_point = before_point + point_change
        time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        target_user = target_user.id
        target_user_name = target_user.name
        user = user.id
        user_name = user.name
        context = good
        cursor.execute(
            "INSERT INTO review_logs (time, target_user, target_user_name, user, user_name, context, Before_point, After_point) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (time, target_user, target_user_name, user, user_name, context, before_point, after_point)
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        (f"SQLite error: {e}")
        return False



# 전체 흐름 함수에서 변경할 점 (변동값 소수 처리)
async def main(good: bool, target_user: discord.Member, user: discord.Member, channel: discord.TextChannel):
    if not await check_in_db(target_user):
        print(f"타겟 유저가 db에 없음: {target_user.name}({target_user.id})")
        await add_user(target_user)
    if not await check_in_db(user):
        print(f"유저가 db에 없음 : {user.name}({user.id})")
        await add_user(user)

    point_change = 0.5 if good else -0.5
    await chainge_point(target_user, point_change)
    await channel.send(f"{user.mention}님이 후기를 제출했습니다.")
