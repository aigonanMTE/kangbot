import discord
from discord import app_commands
from discord.ext import commands
from commands.send_verification_message import send_verification_message
import os
from dotenv import load_dotenv, find_dotenv
env_path = find_dotenv()
print(f"현재 사용 중인 .env 파일 경로: {env_path}")
# 환경 변수 로드
load_dotenv()

discord_token = os.getenv("DISCORD_TOKEN")
print(f"Discord Token: {discord_token}")

intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 접근 허용
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 봇이 준비되었을 때 호출
@bot.event
async def on_ready():
    print(f"봇이 로그인되었습니다: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}개")
    except Exception as e:
        print(e)

TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))  # 감시할 채널 ID를 여기에 입력하세요
TARGET_CHANNEL_ID_2 = int(os.getenv("TARGET_CHANNEL_ID_2"))

@bot.event
async def on_message(message):
    # 자기 자신 메시지 무시
    if message.author == bot.user:
        return

    # 첫 번째 채널에서 메시지 감지 및 임베드 처리
    if message.channel.id == TARGET_CHANNEL_ID:
        last_embed_message = None
        async for msg in message.channel.history(limit=20):
            if (
                msg.author == bot.user
                and msg.embeds
                and msg.embeds[0].title == "그거 아시나요?"
            ):
                last_embed_message = msg
                break

        if last_embed_message:
            try:
                await last_embed_message.delete()
            except Exception:
                pass

        embed = discord.Embed(
            title="그거 아시나요?",
            description='# 19일 부터 서버 봇을 이용한 디스코드 계정과 로블록스 계정연동이 의무화 됩니다.\n - /로블록스_연동 명령어를 사용해 19일 전까지 연동을 완료 해주세요! 미연동시 거래채널에 메시지 보내기 및 거래채널 보기가 불가 합니다\n\n - /거래요청 명령어를 사용해 서버 자체 dm 기능을 사용해보세요!\n - 15줄 넘는 글을 보내려면 거래 포럼 채널 에서 해주세요!',
            color=discord.Color.yellow()
        )
        await message.channel.send(embed=embed)

    # 두 번째 채널에서 메시지 감지 및 임베드 처리
    if message.channel.id == TARGET_CHANNEL_ID_2:
        last_embed_message = None
        async for msg in message.channel.history(limit=20):
            if (
                msg.author == bot.user
                and msg.embeds
                and msg.embeds[0].title == "그거 아시나요?"
            ):
                last_embed_message = msg
                break

        if last_embed_message:
            try:
                await last_embed_message.delete()
            except Exception:
                pass

        embed = discord.Embed(
            title="그거 아시나요?",
            description='# 19일 부터 서버 봇을 이용한 디스코드 계정과 로블록스 계정연동이 의무화 됩니다.\n - /로블록스_연동 명령어를 사용해 19일 전까지 연동을 완료 해주세요! 미연동시 거래채널에 메시지 보내기 및 거래채널 보기가 불가 합니다\n\n - /거래요청 명령어를 사용해 서버 자체 dm 기능을 사용해보세요!\n - 15줄 넘는 글을 보내려면 거래 포럼 채널 에서 해주세요!',
            color=discord.Color.yellow()
        )
        await message.channel.send(embed=embed)

    # 명령어 처리
    await bot.process_commands(message)

# /테스트 커맨드 등록
@bot.tree.command(name="테스트", description="테스트 명령어입니다.")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("테스트",ephemeral=True)

@bot.tree.command(name="ping", description="Ping 명령어입니다.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms" ,ephemeral=True)

@bot.tree.command(name="인증", description="인증 하기")
async def verification_command(interaction: discord.Interaction):
    await send_verification_message(interaction)

from commands.roblox_auth.roblox_auth_command import roblox_auth_command
@bot.tree.command(name="로블록스_연동", description="로블록스 계정과 디스코드 계정을 연동합니다")
@app_commands.describe(roblox_username="연동할 로블록스 유저네임을 입력하세요")
async def roblox_link_command(interaction: discord.Interaction, roblox_username:str):
    await roblox_auth_command(roblox_username,interaction)

from commands.requset.check_my_requests import check_my_requests
from commands.requset.check_trade_requset import check_trade_requset
@bot.tree.command(name="거래확인", description="거래 요청을 확인합니다")
@app_commands.describe(my_requests="자신이 보낸 거래 요청을 확인합니다 확인 하려면 아무거나 입력하세요")
async def check_trade_request_command(interaction: discord.Interaction, my_requests: str = None):
    if not my_requests:  # 값이 없거나 빈 문자열일 때
        await check_trade_requset(interaction)
    else:
        await check_my_requests(interaction)

from commands.requset.refusal_request import refusal_req
@bot.tree.command(name="거래거절", description="거래 요청을 거절합니다")
@app_commands.describe(request_id="거절할 거래 요청의 아이디값을 입력하세요")
async def refusal_request_command(interaction: discord.Interaction, request_id: int):
    await refusal_req(interaction, request_id)

from commands.requset.accepted_requests import accepted_requests_command
@bot.tree.command(name="거래수락", description="거래 요청을 수락합니다")
@app_commands.describe(request_id="수락할 거래요청의 아이디값을 입력하세요")
async def accepted_requests_commandd(interaction: discord.Interaction, request_id: int):
    await accepted_requests_command(interaction, request_id)

from commands.requset.cancel_request import cancel_request
@bot.tree.command(name="거래취소", description="거래 요청을 취소합니다")
@app_commands.describe(request_id="취소할 거래요청의 아이디값을 입력하세요")
async def accepted_requests_commandd(interaction: discord.Interaction, request_id: int):
    await cancel_request(interaction, request_id)


# from commands.open_new_chat import open_new_chat_command
# @bot.tree.command(name="거래체팅", description="상대와의 거래 체팅을 엽니다")
# @app_commands.describe(user="거래할 유저를 선택하세요")
# async def trade_chat_command(interaction: discord.Interaction , user: discord.Member):
#     await open_new_chat_command(interaction, user)

from commands.requset.send_trade_request import send_trade_request_command
@bot.tree.command(name="거래요청", description="거래 요청을 보냅니다")
@app_commands.describe(target_user="거래요청을 보낼 유저 선텍")
async def send_trade_request_commandd(interaction: discord.Interaction, target_user: discord.Member):
    await send_trade_request_command(interaction, target_user)

from commands.register_command import register_command
@bot.tree.command(name="가입", description="서비스 약관에 동의 및 가입진행")
async def register_commandd(interaction: discord.Interaction):
    await register_command(interaction)

from commands.get_point_rank import get_point_rank
@bot.tree.command(name="포인트랭크", description="포인트 랭크을 조회합니다")
@app_commands.describe(user="조회할 유저를 입력하세요")
async def get_point_rank_command(interaction: discord.Interaction, user: discord.Member):
    await get_point_rank(interaction, user)


bot.run(f"{discord_token}")