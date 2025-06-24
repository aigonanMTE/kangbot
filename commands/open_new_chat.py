import discord
from discord.ext import commands
import datetime
from .sql import review, register


async def open_new_chat_command(interaction: discord.Interaction, user: discord.Member):
    if user == interaction.user:
        await interaction.response.send_message("자기 자신과 거래할 수 없습니다.", ephemeral=True)
        return
    if interaction.user.get_role(1383322911926124544) is None or user.get_role(1383322911926124544) is None:
        await interaction.response.send_message("인증되지 않은 유저입니다.", ephemeral=True)
        return

    try:
        guild = interaction.guild

        review_log_channel_id = 1383496377530712288
        review_log_channel = guild.get_channel(review_log_channel_id)

        trade_admin_role_id = 1383489321411285032
        trade_admin_role = guild.get_role(trade_admin_role_id)

        trade_category_id = 1383487342664482907
        trade_category = guild.get_channel(trade_category_id)

        trade_closed_category_id = 1383493549831618680
        trade_closed_category = guild.get_channel(trade_closed_category_id)

        trade_log_channel_id = 1383499310682869894
        trade_log_channel = guild.get_channel(trade_log_channel_id)

        existing_channels = [
            channel for channel in trade_category.text_channels
            if interaction.user.id in channel.id and user.id in channel.id
        ]

        if existing_channels:
            await interaction.response.send_message(f"이미 생성된 거래방이 있습니다: {existing_channels[0].mention}", ephemeral=True)
            return

        timestamp = datetime.datetime.now().strftime("%m%d-%H%M")
        new_channel_name = f"거래-{interaction.user.id}&{user.id}-{timestamp}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            trade_admin_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=new_channel_name,
            category=trade_category,
            overwrites=overwrites
        )

        await trade_log_channel.send(
            f"{user.mention} 님과 {interaction.user.mention} 님의 거래 채널이 생성되었습니다: {channel.mention}"
        )
        await interaction.response.send_message(
            f"{user.mention} 님과 {interaction.user.mention} 님의 거래 채널이 생성되었습니다: {channel.mention}", ephemeral=True
        )

        class TradeEndView(discord.ui.View):
            def __init__(self, channel_to_edit, member1, member2, admin_role, closed_category):
                super().__init__(timeout=None)
                self.channel_to_edit = channel_to_edit
                self.member1 = member1
                self.member2 = member2
                self.admin_role = admin_role
                self.closed_category = closed_category
                self.reviewed_members = set()

            @discord.ui.button(label="거래 종료", style=discord.ButtonStyle.danger, custom_id="trade:end_request")
            async def end_trade(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                # 거래 종료 요청을 누른 사람이 거래 당사자인지 확인
                if interaction_button.user not in [self.member1, self.member2]:
                    await interaction_button.response.send_message("당신은 이 거래의 당사자가 아닙니다.", ephemeral=True)
                    return

                # 바로 종료 처리
                await self.channel_to_edit.send("한 명의 요청으로 거래가 종료되었습니다. 거래방을 종료 카테고리로 이동합니다.")
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
                await trade_log_channel.send(f"{self.member1.mention} 님과 {self.member2.mention} 님의 거래가 종료되었습니다.")
                await interaction_button.response.send_message("거래방이 즉시 종료되었습니다.", ephemeral=True)
                self.stop()
                
            @discord.ui.button(label="상대 후기 남기기", style=discord.ButtonStyle.primary, custom_id="trade:leave_review")
            async def leave_review(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                if interaction_button.user in self.reviewed_members:
                    await interaction_button.response.send_message("이미 후기를 작성하셨습니다.", ephemeral=True)
                    return
                
                target_user = self.member2 if interaction_button.user == self.member1 else self.member1

                if not await register.check_registered(interaction_button.user):
                    await interaction_button.response.send_message(f"{interaction_button.user.mention}님이 가입되지 않았습니다```/가입````명령어를 입력해 약관에 동의후 진행해주세요")
                    return
                if not await register.check_registered(target_user):
                    await interaction_button.response.send_message(f"{target_user}님이 가입되지 않았습니다```/가입````명령어를 입력해 약관에 동의후 진행해주세요")
                    return


                class ReviewChoiceView(discord.ui.View):
                    def __init__(self, parent_view, reviewer, target_user):
                        super().__init__(timeout=60)
                        self.parent_view = parent_view
                        self.reviewer = reviewer
                        self.target_user = target_user

                    @discord.ui.button(label="좋았어요 👍", style=discord.ButtonStyle.success,custom_id="trade:good")
                    async def good_review(self, inner_interaction: discord.Interaction, button: discord.ui.Button):
                        if inner_interaction.user != self.reviewer:
                            await inner_interaction.response.send_message("당신의 버튼이 아닙니다.", ephemeral=True)
                            return
                        await review.main(
                            True,
                            self.target_user,
                            self.reviewer,  # 평가자
                            self.parent_view.channel_to_edit  # 거래 채널
                        )
                        await review_log_channel.send(
                            f"📢 후기: {self.reviewer.mention} → {self.target_user.mention} : **좋았어요 👍**\n {self.target_user.mention}의 포인트 : {await review.get_point(self.target_user)}"
                        )
                        await trade_log_channel.send(
                            f"{self.reviewer.mention} 님이 {self.target_user.mention} 님에게 후기를 남겼습니다"
                        )
                        self.parent_view.reviewed_members.add(self.reviewer)
                        # await inner_interaction.response.send_message("후기를 제출했습니다.", ephemeral=True)
                        self.stop()

                    @discord.ui.button(label="싫었어요 👎", style=discord.ButtonStyle.danger,custom_id="trade:notgood")
                    async def bad_review(self, inner_interaction: discord.Interaction, button: discord.ui.Button):
                        if inner_interaction.user != self.reviewer:
                            await inner_interaction.response.send_message("당신의 버튼이 아닙니다.", ephemeral=True)
                            return
                        await self.parent_view.channel_to_edit.send(
                            f"📢 {self.reviewer.mention}님이 {self.target_user.mention}님의 후기 작성 완료!"
                        )
                        await review.main(
                            False,
                            self.target_user,
                            self.reviewer,  # 평가자
                            self.parent_view.channel_to_edit  # 거래 채널
                        )
                        await review_log_channel.send(
                            f"📢 후기: {self.reviewer.mention} → {self.target_user.mention} : **싫었어요 👎**\n {self.target_user.mention}의 포인트 : {await review.get_point(self.target_user)}"
                        )
                        self.parent_view.reviewed_members.add(self.reviewer)
                        # await inner_interaction.response.send_message("후기를 제출했습니다.", ephemeral=True)
                        self.stop()

                review_view = ReviewChoiceView(self, interaction_button.user, target_user)
                await interaction_button.response.send_message("어떤 후기를 남기시겠습니까?", view=review_view, ephemeral=True)

        view = TradeEndView(channel, interaction.user, user, trade_admin_role, trade_closed_category)

        await channel.send(
            f"{interaction.user.mention}님과 {user.mention}님의 거래방입니다.\n"
            f"거래가 완료되면 '거래 종료 요청' 버튼을 눌러 투표를 시작하거나, 상대 후기를 남길 수 있습니다.",
            view=view
        )

    except discord.Forbidden:
        await interaction.response.send_message("채널 생성 권한이 없습니다.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"오류 발생: {str(e)}", ephemeral=True)
