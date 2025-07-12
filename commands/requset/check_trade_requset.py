from commands.sql import request
from commands.sql import register
import discord
import math

class TradeRequestView(discord.ui.View):
    def __init__(self, requests, page=1):
        super().__init__(timeout=120)
        self.requests = requests
        self.page = page
        self.max_page = max(1, math.ceil(len(requests) / 5))

    async def update_message(self, interaction):
        embed = make_trade_request_embed(self.requests, self.page, self.max_page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="이전", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="다음", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_page:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.defer()

def make_trade_request_embed(requests, page, max_page):
    start = (page - 1) * 5
    end = start + 5
    page_requests = requests[start:end]

    desc = f"거래 요청 [{page}|{max_page}]\n"
    for i, req in enumerate(page_requests, start=1):
        desc += (
            f"====={i}======\n"
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
    return embed

async def check_trade_requset(interaction: discord.Interaction):
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

    requests = await request.get_requests(user)
    if not requests:
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m거래 요청이 없습니다.[0m[2;31m[0m\n```",
            ephemeral=True)
        return

    # 'waiting' 상태만 필터링 및 최신순 정렬
    filtered_requests = [req for req in requests if req['status'] == 'waiting']
    filtered_requests.sort(key=lambda x: x['time'], reverse=True)

    if not filtered_requests:
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m표시할 거래 요청이 없습니다.[0m[2;31m[0m\n```",
            ephemeral=True)
        return

    view = TradeRequestView(filtered_requests)
    embed = make_trade_request_embed(filtered_requests, 1, view.max_page)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)