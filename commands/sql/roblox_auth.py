import discord
import sqlite3
import os
import discord

db_path = os.getenv("ROBLOX_AUTH_DATABASE_PATH")

async def add_user(discord_user: discord.Member, roblox_id: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO auth_users (discord_id, roblox_id) VALUES (?, ?);",
                       (discord_user.id, roblox_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"유저 {discord_user.name}는 이미 등록되어 있습니다.")
        return f"유저 {discord_user.name}는 이미 등록되어 있습니다."
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        return "데이터베이스 오류가 발생했습니다."
    finally:
        conn.close()

async def get_user_2_discord_id(discord_id: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT discord_id FROM auth_users WHERE discord_id = ?;", (discord_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        return None
    except:
        print("알 수 없는 오류 발생")
        return None
    finally:
        conn.close()
    
async def get_user_2_roblox_id(roblox_id: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT roblox_id FROM auth_users WHERE roblox_id = ?;", (roblox_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        return None
    except:
        print("알 수 없는 오류 발생")
        return None
    finally:
        conn.close()