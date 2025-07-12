import discord
import math
from commands.sql import request

class MyRequestView(discord.ui.View):
    def __init__(self, requests, page=1):
        super().__init__(timeout=120)
        self.requests = requests
        self.page = page
        self.max_page = max(1, math.ceil(len(requests) / 5))

    async def update_message(self, interaction):
        embed = make_my_request_embed(self.requests, self.page, self.max_page)
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

def make_my_request_embed(requests, page, max_page):
    start = (page - 1) * 5
    end = start + 5
    page_requests = requests[start:end]

    desc = f"내가 보낸 거래 요청 [{page}|{max_page}]\n"
    for i, req in enumerate(page_requests, start=1):
        # 상태 한글 변환
        status = "대기중" if req['status'] == 'waiting' else (
            "수락됨" if req['status'] == 'accepted' else (
            "거절됨" if req['status'] == 'refused' else (
            "취소됨" if req['status'] == 'cancelled' else (
            "종료됨" if req['status'] == 'ended' else req['status']
        ))))
        desc += (
            f"====={i}======\n"
            f"상대 : <@{req['target_user_id']}>\n"
            f"시간 : {req['time']}\n"
            f"상태 : {status}\n"
            f"요청 아이디 : {req['request_id']}\n"
        )
    desc += "==========="

    embed = discord.Embed(
        title="내가 보낸 거래 요청 목록",
        description=desc,
        color=discord.Color.blue()
    )
    return embed

async def check_my_requests(interaction: discord.Interaction):
    user = interaction.user
    requests = await request.get_my_requests(user)
    if not requests:
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m보낸 거래 요청이 없습니다.[0m[2;31m[0m\n```",
            ephemeral=True)
        return

    # 최신순 정렬
    requests.sort(key=lambda x: x['time'], reverse=True)

    view = MyRequestView(requests)
    embed = make_my_request_embed(requests, 1, view.max_page)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
