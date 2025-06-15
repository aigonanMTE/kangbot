import discord
import sqlite3
async def check_in_db(user : discord.Member):
    try:
        conn = sqlite3.connect('discord_kangbot/DB/user.db')
        cursor = conn.cursor()
        
        # 유저의 ID로 데이터 조회
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
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
    conn = sqlite3.connect('discord_kangbot/DB/user.db')
    cursor = conn.cursor()
    try:
        # 유저가 DB에 존재하는지 확인
        if await check_in_db(user):
            return False  # 이미 존재하는 유저

        # 유저 추가
        cursor.execute("INSERT INTO users (user_id, point , scamer) VALUES (?, ?,?)", (user.id, 35 , 0))
        conn.commit()
        conn.close()
        return True  # 유저 추가 성공
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    
    
async def get_point(user : discord.Member):
    conn = sqlite3.connect('discord_kangbot/DB/user.db')
    cursor = conn.cursor()
    
    # 유저의 ID로 데이터 조회
    cursor.execute("SELECT point FROM users WHERE user_id = ?", (user.id,))
    result = cursor.fetchone()

    conn.close()
    if result:
        return result[0]  # 포인트 반환
    else:
        return False  
    
async def chainge_point(user : discord.member, point : int):
    try:
        conn = sqlite3.connect('discord_kangbot/DB/user.db')
        cursor = conn.cursor()
        get_point_value = await get_point(user)
        new_point = get_point_value + point

        chainge_values = "update user_reviews set point = ? where discord_id = ?"
        cursor.execute(chainge_values, (new_point, user.id))
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    

async def main(good:bool , user:discord.Member):
    if not await check_in_db(user):
        if not await add_user(user):
            print("유저 추가 실패")
        else:
            print("유저 추가 성공")
    else:
        print("유저가 이미 존재합니다.")
    if good:
        await chainge_point(user, 0.5)
    if not good:
        await chainge_point(user, -0.5) 
    



        
        
