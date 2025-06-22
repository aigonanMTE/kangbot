import discord
import sqlite3
import os
import discord
from discord.ext import commands

#asddddddddddddddd
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../DB/user.db'))

async def check_in_db(user : discord.Member):
    try:
        # print(f"DB Path: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 유저의 ID로 데이터 조회
        cursor.execute("SELECT * FROM user_reviews WHERE discord_id = ?", (user.id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return True  # 유저가 DB에 존재함
        else:
            return False  # 유저가 DB에 없음
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    
async def add_user(user : discord.member):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # 유저가 DB에 존재하는지 확인
        if await check_in_db(user):
            return False  # 이미 존재하는 유저

        # 유저 추가
        cursor.execute("INSERT INTO user_reviews (discord_id, point , scamer) VALUES (?, ?,?)", (user.id, 35 , 0))
        conn.commit()
        conn.close()
        return True  # 유저 추가 성공
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    
    
async def get_point(user : discord.Member):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 유저의 ID로 데이터 조회
    cursor.execute("SELECT point FROM user_reviews WHERE discord_id = ?", (user.id,))
    result = cursor.fetchone()

    conn.close()
    if result:
        return result[0]  # 포인트 반환
    else:
        return False  
    
async def chainge_point(user : discord.member, point : int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        get_point_value = await get_point(user)
        new_point = get_point_value + point
        print(f"새로운 포인트: {new_point}")

        chainge_values = "update user_reviews set point = ? where discord_id = ?"
        cursor.execute(chainge_values, (new_point, user.id))
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    

async def main(good:bool , target_user:discord.Member ,user:discord.Member , channel:discord.TextChannel):
    if not await check_in_db(target_user):
        add_user(target_user)
    if not await check_in_db(user):
        add_user(user)

    if good:
        await chainge_point(target_user, 0.5)
        await user.response.send_message("후기를 제출했습니다.", ephemeral=True)
    if not good:
        await chainge_point(target_user, -0.5) 
        await user.response.send_message("후기를 제출했습니다.", ephemeral=True)
    
    
        
        
