from commands.sql import request
from commands.sql import register
import discord

async def refusal_req(interaction: discord.Interaction, request_id: int):
    user = interaction.user
    if user.get_role(1383322911926124544) is None:
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m거래 요청을 확인하려면 유저 역활이 필요합니다 /인증 명령어로 인증을 진행 해주세요[0m[2;31m[0m\n```",
            ephemeral=True)
        return

    if not await register.check_registered(user):
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m거래 요청을 확인하려면 먼저 /가입 명령어로 가입을 진행해주세요[0m[2;31m[0m\n```",
            ephemeral=True)
        return
    
    if not await request.refusal_request(request_id, user.id):
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m당신의 거래가 아니거나 오류가 발생하였습니다[0m[2;31m[0m\n```", ephemeral=True
        )
        return
    else:
        await interaction.response.send_message(
            f"```ansi\n[2;31m[1;31m거래 요청을 거절하였습니다. 거래 요청 아이디: {request_id}[0m[2;31m[0m\n```",
            ephemeral=True
        )
    
