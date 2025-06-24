import discord
from discord.ext import commands
from .sql import review, register

# 0 ~ 11 아이언
# 12 ~ 22 브론즈
# 23 ~ 33 실버
# 34 ~ 44 골드
# 45 ~ 55 플래티넘
# 56 ~ 66 다이아
# 67 ~ 77 초월자
# 78 ~ 99 불멸
# 100 ~ 250 레디언트
# 251 ~ 500 첼린저
# 501 이상 G.O.D

async def get_point_rank(interaction: discord.Interaction, user: discord.Member):
    if not await register.check_registered(user):
        await interaction.response.send_message(f"{user.mention}님은 가입되지 않았습니다", ephemeral=True)
        return
    if not await review.check_in_db(user):
        await interaction.response.send_message(f"{user.mention}님은 후기를 받은적이 없습니다", ephemeral=True)
        return
    
    point = await review.get_point(user)
    if not point:
        await interaction.response.send_message(f"{user.mention}님의 포인트를 조회할 수 없습니다.", ephemeral=True)
        return
    
    if 0 < point <= 11:
        rank = "아이언<:iron:1387053941857976380>"
    elif 12 <= point <= 22:
        rank = "브론즈<:bronz:1387053930466250882>"
    elif 23 <= point <= 33:
        rank = "실버<:selver:1387053900183376086>"
    elif 34 <= point <= 44:
        rank = "골드<:gold:1387053886522523678>"
    elif 45 <= point <= 55:
        rank = "플래티넘<:platium:1387053875340775424>"
    elif 56 <= point <= 66:
        rank = "다이아<:daiamond:1387053857494011936>"
    elif 67 <= point <= 77:
        rank = "초월자<:Ascendant:1387053838938406922>"
    elif 78 <= point <= 99:
        rank = "불멸<:Immortal:1387053825134694492>"
    elif 100 <= point <= 250:
        rank = "레디언트<:Radiant:1387053744251863270>"
    elif 251 <= point <= 500:
        rank = "첼린저<:Challenger:1387055056163180584>"
    elif point >= 501:
        rank = "G.O.D<:grandmaster:1387055449714462840>"
    else:
        rank = "알수 없음 (포인트가 음수이거나 비정상적임)"

    await interaction.response.send_message(
        f"{user.mention}님의 \n랭크: {rank}",
        ephemeral= True
    )
    