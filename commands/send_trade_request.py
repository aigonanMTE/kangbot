import discord
from .sql import register

async def send_trade_request_command(interaction: discord.Interaction, target_user: discord.Member):
    user = interaction.user
    if user.get_role(1383322911926124544) is None:
        await interaction.response.send_message("거래 요청을 보내려면 유저 역활이 필요합니다 /인증 명령어로 인증을 진행 해주세요", ephemeral=True)
        return
    if target_user.get_role(1383322911926124544) is None:
        await interaction.response.send_message("상대 유저가 인증되지 않았습니다", ephemeral=True)
        return
    if not register.check_registered(user):
        await interaction.response.send_message("거래 요청을 보내려면 먼저 /가입 명령어로 가입을 진행해주세요", ephemeral=True)
        return
    if not register.check_registered(target_user):
        await interaction.response.send_message("상대 유저가 가입되지 않았습니다", ephemeral=True)
        return
    
    
