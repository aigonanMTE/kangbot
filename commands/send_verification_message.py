import discord
from discord import app_commands
from discord.ext import commands
import random
import copy

# 원본 문제 리스트
context_list = {
    1: ["아버지가", "가방에", "들어가신다"],
    2: ["디스코비", "0.000000001에", "급구", "합니다"],
    3: ["잠자리", "13123만원에", "급처", "합니다"],
    4: ["인간이", "가장", "큰", "공포를", "느끼는", "11미터", "번지점프"],
    5: ["라쿤", "0.8에", "급처", "합니다"],
    6: ["PS5", "30에", "급처", "합니다"],
    7: ["도라에몽", "타임머신", "1억에", "급처", "합니다"],
    8: ["고양이", "무료로", "분양", "합니다"],
    9: ["RTX4090", "50에", "급처", "합니다"],
    10: ["한정판", "스니커즈", "70에", "급처", "합니다"],
    11: ["이세계", "전생권", "1회", "사용권", "급처", "합니다"],
    12: ["치킨", "쿠폰", "10장", "묶어서", "팝니다"],
    13: ["우주선", "20억에", "급처", "합니다"]
}

# 유저별 정답 저장
user_answers = {}

async def send_verification_message(interaction: discord.Interaction):
    problem_id = random.randint(1, 13)
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

    for opt in options:
        option_button = discord.ui.Button(label=opt[:80], style=discord.ButtonStyle.secondary)

        async def option_callback(interaction_button: discord.Interaction, selected=opt, view=view):
            try:
                answer = user_answers.get(interaction_button.user.id)
                if not answer:
                    await interaction_button.response.send_message("먼저 문제를 받아주세요.", ephemeral=True)
                    return

                if selected == answer:
                    await interaction_button.response.send_message("정답입니다! 🎉", ephemeral=True)
                    role = interaction.guild.get_role(1383322911926124544)
                    if role:
                        await interaction.user.add_roles(role)
                else:
                    await interaction_button.response.send_message("틀렸습니다. 다시 시도하세요!", ephemeral=True)

                user_answers.pop(interaction_button.user.id, None)
            except Exception as e:
                await interaction_button.response.send_message("오류가 발생했습니다", ephemeral=True)
            finally:
                view.stop()

        option_button.callback = option_callback
        view.add_item(option_button)

    await interaction.response.send_message(
        f"다음 문장을 올바른 순서로 배열한 것을 선택하세요 \n예시 : 한정판 삼성 자생슈트 10억에 급처 합니다",
        view=view,
        ephemeral=True
    )
