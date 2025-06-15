import discord
from discord import app_commands
from discord.ext import commands
from commands.send_verification_message import send_verification_message

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

from commands.open_new_chat import open_new_chat_command
@bot.tree.command(name="거래체팅", description="상대와의 거래 체팅을 엽니다")
@app_commands.describe(user="거래할 유저를 선택하세요")
async def trade_chat_command(interaction: discord.Interaction , user: discord.Member):
    await open_new_chat_command(interaction, user)

# 자신의 봇 토큰으로 교체하세요
bot.run("MTM4MzQ0Mzk3OTE5ODE0MDU2OQ.GSB7Mv.OXF23JMY_14FZGSqEsmh14_ywvjQUCSY5JSErs")
