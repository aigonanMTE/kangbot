import os
import logging

testmod = os.getenv("TESTMOD")
token = os.getenv("DISCORD_TOKEN")
url = os.getenv("DATABASE_URL")
log = logging.getLogger(__name__)

async def check_value():
    if token is None:
        log.warning("디스코드 토큰이 설정되지 않았습니다.")
        return False
    if url is None:
        log.warning("데이터베이스 URL이 설정되지 않았습니다.")
        return False
    
async def check_testmod():
    if testmod is None:
        log.warning("테스트모드 환경변수가 설정되지 않았습니다.")
        return False
    elif testmod:
        log.log("테스트 모드가 활성화 되었습니다")
        return False
    elif not testmod:
        log.log("테스트 모드가 비활성화 되었습니다")
        return False
    

    