import discord
import datetime
from commands.sql import request
from commands.sql import review

async def accepted_requests_command(interaction: discord.Interaction, request_id: int):
    guild = interaction.guild
    user = interaction.user

    # 요청한 유저 ID 조회 및 멤버 객체 변환
    target_user_id = await request.get_user(request_id)
    if target_user_id is None:
        await interaction.response.send_message("요청한 유저를 찾을 수 없습니다.", ephemeral=True)
        return
    target_user = await guild.fetch_member(int(target_user_id))

    # 거래 카테고리 및 채널명 생성
    trade_category_id = 1383487342664482907
    trade_category = guild.get_channel(trade_category_id)
    timestamp = datetime.datetime.now().strftime("%m%d-%H%M")
    new_channel_name = f"거래-{user.id}-{target_user.id}-{timestamp}"

    # 이미 거래방이 있는지 확인
    existing_channels = [
        channel for channel in trade_category.text_channels
        if str(user.id) in channel.name and str(target_user.id) in channel.name
    ]
    if existing_channels:
        await interaction.response.send_message(
            f"이미 생성된 거래방이 있습니다: {existing_channels[0].mention}", ephemeral=True
        )
        return

    # 거래요청 수락
    answer = await request.accept_request(request_id, user)
    if answer is False:
        await interaction.response.send_message(
            "```ansi\n[2;31m[1;31m당신의 거래가 아니거나 오류가 발생하였습니다\n거래요청은 /거래확인 명령어로 확인할수 있습니다[0m[2;31m[0m\n```", ephemeral=True
        )
        return

    # 거래방 생성
    await create_new_trade_chat(interaction, target_user, request_id)

class TradeEndView(discord.ui.View):
    def __init__(self, channel_to_edit, member1, member2, admin_role, closed_category, request_id):
        super().__init__(timeout=None)
        self.channel_to_edit = channel_to_edit
        self.member1 = member1
        self.member2 = member2
        self.admin_role = admin_role
        self.closed_category = closed_category
        self.reviewed_members = set()
        self.request_id = request_id

    @discord.ui.button(label="거래 종료", style=discord.ButtonStyle.danger)
    async def end_trade(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user not in [self.member1, self.member2]:
            await interaction_button.response.send_message("거래 당사자만 거래 종료를 요청할 수 있습니다.", ephemeral=True)
            return

        # if len(self.reviewed_members) != 2:
        #     await interaction_button.response.send_message("거래 종료를 위해서는 양쪽 모두 후기를 남겨야 합니다.", ephemeral=True)
        #     return

        await self.channel_to_edit.send("거래가 종료되었습니다. 거래방을 종료 카테고리로 이동합니다.")
        overwrites = {
            self.channel_to_edit.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.member1: discord.PermissionOverwrite(read_messages=False),
            self.member2: discord.PermissionOverwrite(read_messages=False),
            self.admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await self.channel_to_edit.edit(overwrites=overwrites)
        await self.channel_to_edit.edit(category=self.closed_category)
        guild = self.channel_to_edit.guild
        trade_log_channel = guild.get_channel(1383499310682869894)
        await trade_log_channel.send(
            f"{self.member1.mention} 님과 {self.member2.mention} 님의 거래가 종료되었습니다."
        )
        await interaction_button.response.send_message("거래가 종료되었습니다.", ephemeral=True)
        await request.end_request(request_id=self.request_id)
        self.stop()

    @discord.ui.button(label="거래 미진행 종료", style=discord.ButtonStyle.red)
    async def not_trade_end(self, interaction_button: discord.Interaction, button: discord.ui.Button):
        if interaction_button.user not in [self.member1, self.member2]:
            await interaction_button.response.send_message("거래 당사자가 아닙니다", ephemeral=True)
            return

        # 내부 View 클래스 정의
        class NotTradeEndView(discord.ui.View):
            def __init__(self, channel_to_edit, member1, member2, admin_role, closed_category , request_id):
                super().__init__(timeout=30)
                self.channel_to_edit = channel_to_edit
                self.member1 = member1
                self.member2 = member2
                self.admin_role = admin_role
                self.closed_category = closed_category
                self.request_id = request_id

            @discord.ui.button(label="일정 조율 문제", style=discord.ButtonStyle.primary)
            async def end_trade_schedule(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user not in [self.member1, self.member2]:
                    await interaction_button.response.send_message("당신은 이 거래의 당사자가 아닙니다.", ephemeral=True)
                    return

                await self.channel_to_edit.send("거래가 미진행으로 종료되었습니다. 거래방을 종료 카테고리로 이동합니다.")
                overwrites = {
                    self.channel_to_edit.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    self.member1: discord.PermissionOverwrite(read_messages=False),
                    self.member2: discord.PermissionOverwrite(read_messages=False),
                    self.admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                await self.channel_to_edit.edit(overwrites=overwrites)
                await self.channel_to_edit.edit(category=self.closed_category)
                guild = self.channel_to_edit.guild
                trade_log_channel = guild.get_channel(1383499310682869894)
                await review.add_date_problem(interaction_button.user)
                await trade_log_channel.send(
                    f"{self.member1.mention} 님과 {self.member2.mention} 님의 거래가 미진행으로 종료되었습니다."
                )
                await request.end_request(request_id=self.request_id)
                self.stop()

            @discord.ui.button(label="상대가 터무니 없는 가격 제시", style=discord.ButtonStyle.primary)
            async def end_trade_price(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user not in [self.member1, self.member2]:
                    await interaction_button.response.send_message("당신은 이 거래의 당사자가 아닙니다.", ephemeral=True)
                    return

                await self.channel_to_edit.send("거래가 미진행으로 종료되었습니다. 거래방을 종료 카테고리로 이동합니다.")
                overwrites = {
                    self.channel_to_edit.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    self.member1: discord.PermissionOverwrite(read_messages=False),
                    self.member2: discord.PermissionOverwrite(read_messages=False),
                    self.admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                await self.channel_to_edit.edit(overwrites=overwrites)
                await self.channel_to_edit.edit(category=self.closed_category)
                guild = self.channel_to_edit.guild
                trade_log_channel = guild.get_channel(1383499310682869894)
                await review.add_value_problem(interaction_button.user)
                await trade_log_channel.send(
                    f"{self.member1.mention} 님과 {self.member2.mention} 님의 거래가 미진행으로 종료되었습니다."
                )
                await request.end_request(request_id=self.request_id)
                self.stop()

            @discord.ui.button(label="기타", style=discord.ButtonStyle.primary)
            async def end_trade_other(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user not in [self.member1, self.member2]:
                    await interaction_button.response.send_message("당신은 이 거래의 당사자가 아닙니다.", ephemeral=True)
                    return

                await self.channel_to_edit.send("거래가 미진행으로 종료되었습니다. 거래방을 종료 카테고리로 이동합니다.")
                overwrites = {
                    self.channel_to_edit.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    self.member1: discord.PermissionOverwrite(read_messages=False),
                    self.member2: discord.PermissionOverwrite(read_messages=False),
                    self.admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                await self.channel_to_edit.edit(overwrites=overwrites)
                await self.channel_to_edit.edit(category=self.closed_category)
                guild = self.channel_to_edit.guild
                trade_log_channel = guild.get_channel(1383499310682869894)
                await review.add_other_problem(interaction_button.user)
                await trade_log_channel.send(
                    f"{self.member1.mention} 님과 {self.member2.mention} 님의 거래가 미진행으로 종료되었습니다."
                )
                await request.end_request(request_id=self.request_id)
                self.stop()

        await interaction_button.response.send_message(
            "거래를 종료하는 사유가 무엇인가요?",
            ephemeral=True,
            view=NotTradeEndView(
                self.channel_to_edit,
                self.member1,
                self.member2,
                self.admin_role,
                self.closed_category,
                self.request_id
            )
        )

    @discord.ui.button(label="후기 남기기", style=discord.ButtonStyle.success)
    async def review_trade(self, interaction_button: discord.Interaction, button: discord.ui.Button):

        target_user = self.member1 if interaction_button.user == self.member2 else self.member2

        if interaction_button.user not in [self.member1, self.member2]:
            await interaction_button.response.send_message("거래 당사자만 후기를 남길 수 있습니다.", ephemeral=True)
            return

        if interaction_button.user in self.reviewed_members:
            await interaction_button.response.send_message("이미 후기를 남겼습니다.", ephemeral=True)
            return
        
        class ReviewView(discord.ui.View):
            def __init__(self, target_user:discord.member, interaction_user:discord.member, interaction: discord.Interaction, channel:discord.TextChannel, reviewed_members):
                super().__init__(timeout=60)
                self.target_user = target_user
                self.interaction_user = interaction_user
                self.channel = channel
                guild = interaction.guild
                review_log_channel_id = 1383496377530712288
                review_log_channel = guild.get_channel(review_log_channel_id)
                self.review_log_channel = review_log_channel
                self.reviewed_members = reviewed_members

            @discord.ui.button(label="👍", style=discord.ButtonStyle.green)
            async def good_review(self, interaction: discord.Interaction, button: discord.ui.Button):
                await review.main(
                            True,
                            self.target_user,
                            self.interaction_user,  # 평가자
                            self.channel  # 거래 채널
                        )
                await interaction.response.send_message("좋은 후기를 남겼습니다.", ephemeral=True)
                await self.review_log_channel.send(
                            f"📢 후기: {self.interaction_user.mention} → {self.target_user.mention} : **좋았어요 👎**\n {self.target_user.mention}의 포인트 : {await review.get_point(self.target_user)}"
                        )
                self.reviewed_members.add(interaction_button.user)
                self.stop()

            @discord.ui.button(label="👎", style=discord.ButtonStyle.red)
            async def bad_review(self, interaction: discord.Interaction, button: discord.ui.Button):
                await review.main(
                            True,
                            self.target_user,
                            self.interaction_user,  # 평가자
                            self.channel  # 거래 채널
                        )
                await interaction.response.send_message("나쁜 후기를 남겼습니다.", ephemeral=True)
                await self.review_log_channel.send(
                            f"📢 후기: {self.interaction_user.mention} → {self.target_user.mention} : **싫었어요 👎**\n {self.target_user.mention}의 포인트 : {await review.get_point(self.target_user)}"
                        )
                self.reviewed_members.add(interaction_button.user)
                self.stop()

        await interaction_button.response.send_message(
        f"{target_user.mention}님에 대한 후기를 남겨주세요",
        view=ReviewView(
            target_user,
            interaction_button.user,
            interaction_button,
            self.channel_to_edit,
            self.reviewed_members   # 추가!
        ),
            ephemeral=True
        )
        

async def create_new_trade_chat(interaction: discord.Interaction, target_user: discord.Member, request_id: int):
    guild = interaction.guild

    trade_admin_role_id = 1383489321411285032
    trade_admin_role = guild.get_role(trade_admin_role_id)

    trade_category_id = 1383487342664482907
    trade_category = guild.get_channel(trade_category_id)

    trade_closed_category_id = 1383493549831618680
    trade_closed_category = guild.get_channel(trade_closed_category_id)

    trade_log_channel_id = 1383499310682869894
    trade_log_channel = guild.get_channel(trade_log_channel_id)

    timestamp = datetime.datetime.now().strftime("%m%d-%H%M")
    new_channel_name = f"거래-{interaction.user.id}-{target_user.id}-{timestamp}"

    existing_channels = [
        channel for channel in trade_category.text_channels
        if str(interaction.user.id) in channel.name and str(target_user.id) in channel.name
    ]
    if existing_channels:
        await interaction.response.send_message(
            f"이미 생성된 거래방이 있습니다: {existing_channels[0].mention}", ephemeral=True
        )
        return

    # 1. 먼저 응답(임시 안내)
    await interaction.response.send_message(
        f"```ansi\n[2;32m거래 요청을 수락했습니다. (요청 ID: {request_id})[0m\n```"
        "거래 채널을 생성 중입니다...", ephemeral=True
    )

    # 2. 채널 생성
    channel = await guild.create_text_channel(
        name=new_channel_name,
        category=trade_category,
    )

    view = TradeEndView(channel, interaction.user, target_user, trade_admin_role, trade_closed_category, request_id)

    await trade_log_channel.send(
        f"{target_user.mention} 님과 {interaction.user.mention} 님의 거래 채널이 생성되었습니다: {channel.mention}"
    )

    # 3. 거래방 안내 메시지는 생성된 거래방에 전송
    await channel.send(
        f"{interaction.user.mention}님과 {target_user.mention}님의 거래방입니다.\n"
        f"거래가 종료 되면 거래 종료 버튼을 눌러 거래를 종료 할수 있습니다",
        view=view
    )
