from .sql import request
from .sql import register
import discord
import logging

async def check_trade_requset(interaction: discord.Interaction):
    desc = ""
    user = interaction.user
    if user.get_role(1383322911926124544) is None:
        await interaction.response.send_message("```ansi\n[2;31m[1;31m거래 요청을 확인하려면 유저 역활이 필요합니다 /인증 명령어로 인증을 진행 해주세요[0m[2;31m[0m\n```", ephemeral=True)
        return

    if not await register.check_registered(user):
        await interaction.response.send_message("```ansi\n[2;31m[1;31m거래 요청을 확인하려면 먼저 /가입 명령어로 가입을 진행해주세요[0m[2;31m[0m\n```", ephemeral=True)
        return

    requests = await request.get_requests(user)
    if not requests:
        await interaction.response.send_message("```ansi\n[2;31m[1;31m거래 요청이 없습니다.[0m[2;31m[0m\n```", ephemeral=True)
        return

    # 'waiting' 상태만 필터링
    filtered_requests = [req for req in requests if req['status'] == 'waiting']

    if not filtered_requests:
        await interaction.response.send_message("```ansi\n[2;31m[1;31m표시할 거래 요청이 없습니다.[0m[2;31m[0m\n```", ephemeral=True)
        return

    # 최대 3개만 표시
    for i, req in enumerate(filtered_requests[:3]):
        desc += (
            f"====={i+1}======\n"
            f"거래 요청자 : <@{req['user_id']}>\n"
            f"시간 : {req['time']}\n"
            f"상태 : 대기중\n"
            f"요청 아이디 : {req['request_id']}\n"
        )
    desc += "==========="

    embed = discord.Embed(
        title="거래 요청 목록",
        description=desc,
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)