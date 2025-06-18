import discord
import sqlite3
import os
import discord

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../DB/user.db'))

async def check_registered(user:discord.Member):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 유저의 ID로 데이터 조회
    cursor.execute("SELECT * FROM registered_users WHERE discord_id = ?", (user.id,))
    result = cursor.fetchone()

    conn.close()
    
    if result:
        return True  # 유저가 DB에 존재함
    else:
        return False  # 유저가 DB에 없음
    

async def add_user(user: discord.Member):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # 유저가 DB에 존재하는지 확인
        if await check_registered(user):
            return False  # 이미 존재하는 유저

        # 유저 추가
        cursor.execute("INSERT INTO registered_users (discord_id) VALUES (?)", (user.id,))
        conn.commit()
        conn.close()
        return True  # 유저 추가 성공
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False