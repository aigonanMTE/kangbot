import re
import discord
import ro_py
import asyncio
import aiohttp
import random

async def check_user_exists(username: str):#유저 존재 확인 함수임
    client = ro_py.Client()

    try:
        user = await client.get_user_by_username(username)
        print(f"존재하는 사용자입니다: {user.display_name} (ID: {user.id})")
        return True
    except:
        print("존재하지 않는 사용자입니다.")
        return False
    
async def get_user_by_username_safe(username: str):
    client = ro_py.Client()
    try:
        user = await client.get_user_by_username(username)
        return user  # 유저 객체 반환
    except:
        return None
    
async def user_has_item(user_id: int, target_asset_id: int): #아바타 확인 함수임
    url = f"https://avatar.roblox.com/v1/users/{user_id}/avatar"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"오류 발생: {resp.status}")
                return False

            data = await resp.json()
            asset_ids = [asset["id"] for asset in data.get("assets", [])]

            return target_asset_id in asset_ids

async def roblox_auth_command(roblox_name: str, interaction: discord.Interaction):
    chnanel = interaction.channel

    if not roblox_name:
        await interaction.response.send_message("로블록스 유저네임을 입력해주세요.", ephemeral=True)
        return

    # 유저네임 유효성 검사
    is_valid = (
        3 <= len(roblox_name) <= 20 and                      # 길이
        re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", roblox_name) and # 첫 글자 영어, 전체 허용 문자
        "__" not in roblox_name and                          # 연속된 밑줄
        not roblox_name.isdigit()                            # 숫자만으로 구성된 이름 금지
    )

    if not is_valid:
        await interaction.response.send_message("올바르지 않은 로블록스 유저네임 형식입니다.", ephemeral=True)
        return

    # 정규식으로 유저네임 거르고 api로 거를거임
    if not asyncio.run(check_user_exists(roblox_name)):
        await interaction.response.send_message("존재하지 않는 로블록스 유저네임입니다.", ephemeral=True)
        return

    # 유저는 존재하긴 함

    #유저련한테 특정 꽁짜 아이템 하나 끼라하고 그거 꼈으면 프로필 설명으로 인증 할거임
    #인증 아바타 아이템 목록임
    #63690008
    #451221329
    #376527500
    #3656493304
    user = await get_user_by_username_safe(roblox_name)
    if user is None:
        await interaction.response.send_message(f"로블록스 유저 정보를 가져오는 데 실패했습니다.", ephemeral=True)
        return
    itmes = [63690008, 451221329, 376527500, 3656493304] #인증 아이템 목록
    random_item = random.choice(itmes) #랜덤으로 아이템 하나 뽑기

    messages = [
        "шщфавышщо",
        "вдв кдфрадв",
        "ìḀḑṔẲẋẙḧ",
        "ŁîŤřôŠ",
        "ǍğŵüÕč",
        "ĐîẞńėÛ",
        "ŢơďŐč",
        "ĽŕäƁş",
        "ȞôÑťŰ",
        "ǦäŘţŐ",
        "ŘůĿěẞ",
        "ŚïƉâŲ",
        "ŇýČęŰ"
    ]
    message = random.choice(messages) #랜덤으로 아이템 하나 뽑기

    class next_button(discord.ui.Button):
        def __init__(self):
            super().__init__(label="다음단계", style=discord.ButtonStyle.green)
            super().__init__(label="취소", style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            if not await user_has_item(user.id, random_item):
                await interaction.response.send_message("아직 아이템을 착용하지 않았습니다. 아이템을 착용한 후 다시 시도해주세요.", ephemeral=True)
                return
            
            # 인증 완료 처리
            await interaction.response.send_message(f"인증이 완료되었습니다! {roblox_name} 님의 로블록스 유저네임이 확인되었습니다.", ephemeral=True)
    
    await interaction.response.send_message(f"""로블록스 유저네임 : `{roblox_name}` 디스플레이 네임 : `{user.display_name}`이(가) 확인되었습니다.
                                            만약 자신이 아니라면 아레 `취소`버튼을 눌러 취소해주세요
                                            자신이 맞다면 아레 인증 양식을 따라주세요

                                            =====인증 양식=====
                                            1. 자신의 로블록스 [사용자 프로필](https://www.roblox.com/users/1{user.id}/profile)에 들어가 설명을 아레 글로 바꿔주세요
                                            옆 파란 글씨를 클릭해 프로필로 들어갈수 있습니다 => [사용자 프로필](https://www.roblox.com/users/1{user.id}/profile)
                                            ```{message}```

                                            2.아레 파란 글씨를 클릭해 해당 아이템을 구메후 착용해주세요 아이템은 공짜이며 누구나 구메할수 있습니다
                                            [파란 글씨](https://www.roblox.com/catalog/{random_item})

                                            3.위 단계들을 모두 수행후 아레 다음단계 버튼을 눌러주세요
                                            # 🚨주의 사항🚨 : 제한시간은 10분입니다 10분이 지나면 처음부터 다시 진행해야 합니다.""", ephemeral=True, view=discord.ui.View().add_item(next_button()).timeout=600)
                                            

    if not await user_has_item(user.id, random_item):
        print(f"사용자가 아이템을 착용하지 않았습니다: {user.display_name} (ID: {user.id})")
        await chnanel.send(f"사용자가 아이템을 착용하지 않았습니다: {user.display_name} (ID: {user.id})", ephemeral=True)
        return
    elif 
