import discord
from .sql import register
from .sql import review
from .sql import request

async def send_trade_request_command(interaction: discord.Interaction, target_user: discord.Member):
    user = interaction.user
    if user.get_role(1383322911926124544) is None:
        await interaction.response.send_message("```ansi\n[2;31m[1;31m거래 요청을 보내려면 유저 역활이 필요합니다 /인증 명령어로 인증을 진행 해주세요[0m[2;31m[0m\n```", ephemeral=True)
        return
    if target_user.get_role(1383322911926124544) is None:
        await interaction.response.send_message("```ansi\n[2;31m[1;31m상대 유저가 인증되지 않았습니다[0m[2;31m[0m\n```", ephemeral=True)
        return
    if not await register.check_registered(user):
        await interaction.response.send_message("```ansi\n[2;31m[1;31m거래 요청을 보내려면 먼저 /가입 명령어로 가입을 진행해주세요[0m[2;31m[0m\n```", ephemeral=True)
        return
    if not await register.check_registered(target_user):
        await interaction.response.send_message("```ansi\n[2;31m[1;31m상대 유저가 가입되지 않았습니다[0m[2;31m[0m\n```", ephemeral=True)
        return
    
    if user.id == target_user.id:
        await interaction.response.send_message("```ansi\n[2;31m[1;31m자기 자신에게 거래 요청을 보낼 수 없습니다[0m[2;31m[0m\n```", ephemeral=True)
        return
    
    if not await request.add_request(user, target_user):
        await interaction.response.send_message("```ansi\n[2;31m[1;31m거래 요청을 보내는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.[0m[2;31m[0m\n```", ephemeral=True)
        return
    else:
        if await review.get_last_review_time(user) is None:
            await interaction.response.send_message(f"```ansi\n[2;31m[1;31m리뷰를 작성한적이 없는 유저입니다 거래에 주의가 필요할수 있습니다.[0m[2;31m[0m\n```\n```ansi\n[2;32m[2;32m[1;32m{target_user.global_name}님에게 거래 요청을 보냈습니다.[0m[2;32m[0m[2;32m[0m\n```", ephemeral=True)
        else:
            await interaction.response.send_message(f"```ansi\n[2;32m[2;32m[1;32m{target_user.global_name}님에게 거래 요청을 보냈습니다.[0m[2;32m[0m[2;32m[0m\n```", ephemeral=True)
