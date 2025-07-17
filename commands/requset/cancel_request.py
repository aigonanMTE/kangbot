import discord
from commands.sql import request
from commands.sql import register
import logging

async def cancel_request(interaction: discord.Interaction, request_id: int):
    print(f"Cancel request called with request_id: {request_id}")
    user = interaction.user
    if user.get_role(1383322911926124544) is None:
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m거래 요청을 취소하려면 유저 역활이 필요합니다 /인증 명령어로 인증을 진행 해주세요[0m[2;31m[0m\n```",
            ephemeral=True)
        return

    if not await register.check_registered(user):
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m거래 요청을 취소하려면 먼저 /가입 명령어로 가입을 진행해주세요[0m[2;31m[0m\n```",
            ephemeral=True)
        return

    if not await request.cancel_request(request_id, user.id):
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m당신의 거래가 아니거나 오류가 발생하였습니다. 거래요청은 /거래확인 명령어로 확인할수 있습니다.[0m[2;31m[0m\n```", ephemeral=True
        )
        return
    else:
        await interaction.response.send_message(
            f"```ansi\n[2;31m[1;31m거래 요청을 취소하였습니다. 거래 요청 아이디: {request_id}[0m[2;31m[0m\n```",
            ephemeral=True
        )
        logging.info(f"거래 요청 취소됨: 요청 ID {request_id}, 사용자 ID {user.id}")