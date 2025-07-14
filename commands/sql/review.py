import discord
import sqlite3
import os
from discord.ext import commands
import datetime
import logging

# DB 경로 설정
db_path = os.getenv("DATABASE_PATH")
log_db_path = os.getenv("LOG_DATABASE_PATH")

async def add_other_problem(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id = str(user.id)
        
        cursor.execute("select other_problem from user_reviews where discord_id=?;", (user_id,))
        result = cursor.fetchone()

        # 기존 값이 None이면 0으로, 아니면 1 더하기
        if result is None or result[0] is None:
            new_value = 1
        else:
            new_value = int(result[0]) + 1

        cursor.execute("update user_reviews set other_problem=? where discord_id=?;", (new_value, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(f"기타 문제 추가 중 오류 발생\nSQLite error: {e}")
        return False

async def add_value_problem(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id = str(user.id)
        
        cursor.execute("select value_problem from user_reviews where discord_id=?;", (user_id,))
        result = cursor.fetchone()

        # 기존 값이 None이면 0으로, 아니면 1 더하기
        if result is None or result[0] is None:
            new_value = 1
        else:
            new_value = int(result[0]) + 1

        cursor.execute("update user_reviews set value_problem=? where discord_id=?;", (new_value, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(f"가격 조율 문제 추가 중 오류 발생\nSQLite error: {e}")
        return False

async def add_date_problem(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id = str(user.id)
        
        cursor.execute("select date_problem from user_reviews where discord_id=?;", (user_id,))
        result = cursor.fetchone()
        # 기존 값이 None이면 0으로, 아니면 1 더하기
        if result is None or result[0] is None:
            new_value = 1
        else:
            new_value = int(result[0]) + 1

        cursor.execute("update user_reviews set date_problem=? where discord_id=?;", (new_value, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(f"날짜 문제 추가 중 오류 발생\nSQLite error: {e}")
        return False

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
        logging.error(f"review.py의 check_in_db함수에서 오류 발생\n SQLite error: {e}")
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
        logging.error(f"review.py의 add_user함수에서 오류 발생\nSQLite error: {e}")
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
        logging.error(f"review.py의 chainge_point함수에서 오류 발생\nSQLite error: {e}")
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
        logging.error(f"review.py의 add_log함수에서 오류 발생\nSQLite error: {e}")
        return False
    
async def loging_last_review_time(user: discord.Member):
    try:
        time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("update user_reviews set last_review_time=? where discord_id=?", (time,user.id))
        cursor.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"review.py의 loging_last_review_time함수에서 오류 발생\nSQLite error: {e}")
        return False
        

async def get_last_review_time(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT last_review_time FROM user_reviews WHERE discord_id = ?", (user.id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            print(f"마지막 리뷰 시간 조회 성공: {user.name} {result[0]}")
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        logging.error(f"review.py의 get_last_review_time함수에서 오류 발생\nSQLite error: {e}")
        return None

# 전체 흐름 함수에서 변경할 점 (변동값 소수 처리)
async def main(good: bool, target_user: discord.Member, user: discord.Member, channel: discord.TextChannel):
    if not await check_in_db(target_user):
        print(f"타겟 유저가 db에 없음: {target_user.name}({target_user.id})")
        await add_user(target_user)
    if not await check_in_db(user):
        print(f"유저가 db에 없음 : {user.name}({user.id})")
        await add_user(user)
    point_change = 0.5 if good else -0.5
    await add_log(user, target_user, good)
    await chainge_point(target_user, point_change)
    await loging_last_review_time(user)
    await channel.send(f"{user.mention}님이 후기를 제출했습니다.")
