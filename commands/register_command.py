import discord
from .sql import register

async def register_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        """# 서비스 이용 약관
- 최종 수정일 2025/6/17
- 적용 대상 : 이 디스코드 봇(이하 서비스라 칭함)을 사용하는 모든 사용자

**1.서비스 악용 **
- 제공하려는 서비스의 의도에 맞지 않게 사용함을 서비스 악용이라고 정의함
- 서비스 악용시 법적 책임은 사용자에게 있음

**2.수집하는 정보**
- 이 서비스는 다음과 같은 정보를 저장할수 있습니다.
- 사용자의 discord 사용자 id
- 사용자의 discord 정보

**3.정보 수집 목적**
- 사용자의 거래 기록 저장 및 다른 기능을 구현하기 위해
- 봇의 정상적인 기능 유지 및 개선

**4.정보 보관 기간**
- 정보는 사용자가 봇을 사용하는 동안에만 보관되며,    사용자가 요청할 경우 언제든지 삭제할 수 있습니다.

**5.제 3자 제공**
- 어떠한 경우에도 사용자의 정보를 제 3자에게 제공하지 않습니다, 단 아레와 같은 경우에는 사용자의 정보를 제 3자에게 제공할수 있습니다
- 1.국가 수사 기관의  협조 요청

**6.사용자 권리**
- 사용자는 언제든지 자신의 데이터를 수정 , 삭제요청 할수 있습니다.
- 요청 방법 개발자에게 dm (단 수정의 경우 이유가 명확해야함)""",
        ephemeral=True,
        view=AgreeView()
    )
class AgreeView(discord.ui.View):
    @discord.ui.button(label="동의합니다", style=discord.ButtonStyle.success)
    async def agree(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await register.add_user(interaction.user):
            await interaction.response.send_message("약관에 동의하셨습니다!\n가입 완료!", ephemeral=True)
        else:
            await interaction.response.send_message("이미 가입된 사용자거나 서버 오류 발생", ephemeral=True)

