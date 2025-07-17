import discord
from discord import app_commands
from discord.ext import commands
from commands.send_verification_message import send_verification_message
import os

discord_token = os.getenv("DISCORD_TOKEN")
# print(f"Discord Token: {discord_token}")

intents = discord.Intents.default()
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

# 자신의 봇 토큰으로 교체하세요
bot.run(discord_token)
