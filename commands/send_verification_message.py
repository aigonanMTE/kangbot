import discord
from discord import app_commands
from discord.ext import commands
import random
import copy
import os
from dotenv import load_dotenv

load_dotenv()

# 원본 문제 리스트
context_list = {
    1: ["아버지가", "가방을", "들어간다"],
    2: ["나는", "고양이를", "키운다"],
    3: ["나는", "사과를", "먹었다"],
    4: ["강아지가", "공을", "물었다"],
    5: ["나는", "책상을", "닦았다"],
    6: ["나는", "라면을", "끓였다"],
    7: ["나는", "영화를", "봤다"], 
    8: ["나는", "커피를", "마신다"],
    9: ["나는", "자동차를", "운전했다"],
    10: ["나는", "꽃을", "심었다"],
    11: ["나는", "노래를", "불렀다"],
    12: ["나는", "문을", "열었다"],
    13: ["나는", "편지를", "썼다"],
    14: ["파이썬은", "쉬운", "언어다"],
    15: ["러시아어에는", "강세가", "있다"],
    16: ["나는", "오늘도", "논다"],
    17: ["러시아어는", "문법이", "이상하다"],
    18: ["러시아어는", "어려운", "언어다"],
    19: ["일본어는", "한국어와", "비슷하다"]
}


# 유저별 정답 저장
user_answers = {}

async def send_verification_message(interaction: discord.Interaction):
    # 이미 역할이 있는지 확인
    role_id = os.getenv("user_role_id")
    if role_id is not None:
        role = interaction.guild.get_role(int(role_id))
        if role and role in interaction.user.roles:
            await interaction.response.send_message("이미 인증된 유저입니다.", ephemeral=True)
            return

    problem_id = random.randint(1, 19)
    original = context_list[problem_id]
    correct_answer = ' '.join(original)

    # 보기 생성: 정답 + 3개의 랜덤 오답 생성
    options = set()
    options.add(correct_answer)

    while len(options) < 4:
        shuffled = copy.copy(original)
        random.shuffle(shuffled)
        shuffled_text = ' '.join(shuffled)
        options.add(shuffled_text)

    options = list(options)
    random.shuffle(options)

    # 유저의 정답 저장
    user_answers[interaction.user.id] = correct_answer

    class VerificationView(discord.ui.View):
        def __init__(self, timeout=30):
            super().__init__(timeout=timeout)

        async def on_timeout(self):
            await interaction.followup.send("시간이 초과되어 탈락하였습니다. 다시 시도해주세요.", ephemeral=True)
            user_answers.pop(interaction.user.id, None)

    view = VerificationView()

    def make_option_callback(selected_option):
        async def option_callback(interaction_button: discord.Interaction):
            try:
                answer = user_answers.get(interaction_button.user.id)
                if not answer:
                    await interaction_button.response.send_message("먼저 문제를 받아주세요.", ephemeral=True)
                    return

                if selected_option == answer:
                    await interaction_button.response.send_message("정답입니다! 🎉", ephemeral=True)
                    role = interaction.guild.get_role(int(os.getenv("user_role_id")))
                    if role:
                        await interaction.user.add_roles(role)
                else:
                    await interaction_button.response.send_message("틀렸습니다. 다시 시도하세요!", ephemeral=True)

                user_answers.pop(interaction_button.user.id, None)
            except Exception as e:
                await interaction_button.response.send_message("오류가 발생했습니다", ephemeral=True)
            finally:
                view.stop()

        return option_callback

    for opt in options:
        option_button = discord.ui.Button(label=opt[:80], style=discord.ButtonStyle.secondary)
        option_button.callback = make_option_callback(opt)
        view.add_item(option_button)

    await interaction.response.send_message(
        "다음 문장을 아레 순서대로 알맞게 배열한 것을 선택하세요 \n주어 - 목적어 - 서술어(~다)",
        view=view,
        ephemeral=True
    )
