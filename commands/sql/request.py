import sqlite3
import os
import discord
import datetime
import logging

db_path = os.getenv("TRADE_DATABASE_PATH")

async def add_request(user: discord.Member, target_user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id = str(user.id)
        target_user_id = str(target_user.id)
        time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")# 현재 시간을 ISO 형식으로 저장    

        cursor.execute("insert into requests (user, user_id , target_user, target_user_id, time, status) values (?,?,?,?,?,?);", (user.name, user_id, target_user.name, target_user_id, time, "waiting"))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(f"거래 요청 추가중 오류 발생\nSQLite error: {e}")
        return False
    
async def get_my_requests(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id1 = str(user.id)
        cursor.execute("select * from requests where user_id = ? and status = 'waiting';", (user_id1,))
        requests = cursor.fetchall()
        conn.close()

        data = [
            {
                "request_id": request[0],
                "user": request[1],
                "user_id": request[2],
                "target_user": request[3],
                "target_user_id": request[4],
                "time": request[5],
                "status": request[6]
            } for request in requests
        ]
        logging.info(f"거래 요청 조회: {user.name} - 요청 수: {len(data)}")
        if not requests:
            return None

        return data
    except sqlite3.Error as e:
        logging.error(f"거래 요청 조회중 오류 발생\nSQLite error: {e}")
        return None

async def get_requests(user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id1 = str(user.id)
        cursor.execute("select * from requests where target_user_id = ? and status = 'waiting';", (user_id1,))
        requests = cursor.fetchall()
        conn.close()

        data = [
            {
                "request_id": request[0],
                "user": request[1],
                "user_id": request[2],
                "target_user": request[3],
                "target_user_id": request[4],
                "time": request[5],
                "status": request[6]
            } for request in requests
        ]
        logging.info(f"거래 요청 조회: {user.name} - 요청 수: {len(data)}")
        if not requests:
            return None

        return data
    except sqlite3.Error as e:
        logging.error(f"거래 요청 조회중 오류 발생\nSQLite error: {e}")
        return None

async def accept_request(request_id: int, user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        user_id = str(user.id)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM requests WHERE request_id = ? AND status = 'waiting' AND target_user_id=?;", (request_id,user_id))
        request = cursor.fetchone()
        if not request:
            logging.info(f"거래 요청 수락 실패: 요청 ID {request_id} 또는 사용자 ID {user_id}가 잘못되었습니다.")
            conn.close()
            return False
        
        cursor.execute(
            "UPDATE requests SET status = 'accepted' WHERE request_id = ? AND status = 'waiting' AND target_user_id =?;",
            (request_id,user_id)
        )
        conn.commit()
        conn.close()
        logging.info(f"거래 요청 수락 (요청 ID: {request_id})")
        return True
    except sqlite3.Error as e:
        logging.error(f"거래 요청 수락 중 오류 발생\nSQLite error: {e}")
        return False
    
async def refusal_request(request_id: int, user_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM requests WHERE request_id = ? AND status = 'waiting' AND target_user_id=?;", (request_id, str(user_id)))
        request = cursor.fetchone()
        if not request:
            logging.info(f"거래 요청 거절 실패: 요청 ID {request_id} 또는 사용자 ID {user_id}가 잘못되었습니다.")
            conn.close()
            return False
        
        cursor.execute(
            "UPDATE requests SET status = 'refusal' WHERE request_id = ? AND status = 'waiting' AND target_user_id =?;",
            (request_id, str(user_id))
        )
        conn.commit()
        conn.close()
        logging.info(f"거래 요청 거절 (요청 ID: {request_id})")
        return True
    except sqlite3.Error as e:
        logging.error(f"거래 요청 거절 중 오류 발생\nSQLite error: {e}")
        return False
    
async def get_user(request_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM requests WHERE request_id = ?;", (request_id,))
        target_user_id = cursor.fetchone()
        conn.close()

        if target_user_id:
            return int(target_user_id[0])
        else:
            logging.info(f"거래 요청 ID {request_id}에 대한 대상 사용자 ID를 찾을 수 없습니다.")
            return None
    except sqlite3.Error as e:
        logging.error(f"대상 사용자 조회 중 오류 발생\nSQLite error: {e}")
        return None
    
async def dobble_request_check(user: discord.Member, target_user: discord.Member):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        user_id = str(user.id)
        target_user_id = str(target_user.id)

        cursor.execute("SELECT * FROM requests WHERE user_id = ? AND target_user_id = ? AND status = 'waiting';", (user_id, target_user_id))
        request = cursor.fetchone()
        conn.close()

        if request:
            logging.info(f"거래 요청 중복 확인: {user.name} -> {target_user.name} - 중복 요청이 존재합니다.")
            return True
        else:
            logging.info(f"거래 요청 중복 확인: {user.name} -> {target_user.name} - 중복 요청이 없습니다.")
            return False
    except sqlite3.Error as e:
        logging.error(f"거래 요청 중복 확인 중 오류 발생\nSQLite error: {e}")
        return False
    
async def cancel_request(request_id: int, user_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM requests WHERE request_id = ? AND status = 'waiting' AND user_id=?;", (request_id, str(user_id)))
        request = cursor.fetchone()
        if not request:
            logging.info(f"거래 요청 수락 실패: 요청 ID {request_id} 또는 사용자 ID {user_id}가 잘못되었습니다.")
            conn.close()
            return False
        
        cursor.execute(
            "UPDATE requests SET status = 'cancel' WHERE request_id = ? AND status = 'waiting' AND user_id =?;",
            (request_id, str(user_id))
        )
        conn.commit()
        conn.close()
        logging.info(f"거래 요청 취소 (요청 ID: {request_id})")
        return True
    except sqlite3.Error as e:
        logging.error(f"거래 요청 취소 중 오류 발생\nSQLite error: {e}")
        return False

async def end_request(request_id: int):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE requests SET status = 'ended' WHERE request_id = ? AND status = 'accepted';",
            (request_id,)
        )
        conn.commit()
        conn.close()
        logging.info(f"거래 요청 종료 (요청 ID: {request_id})")
        return True
    except sqlite3.Error as e:
        logging.error(f"거래 요청 종료 중 오류 발생\nSQLite error: {e}")
        return
