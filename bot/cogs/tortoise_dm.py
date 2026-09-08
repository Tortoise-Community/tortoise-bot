import asyncio
import datetime
import logging
from typing import Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import discord
from discord.ext import commands, tasks
from discord import app_commands

from bot.constants import (mod_mail_emoji_id, event_emoji_id, staff_application_emoji_id, bug_emoji_id,
                           ban_appeal_server_id, tortoise_guild_id, admin_role_id, mod_mail_ping_role_id,
                           moderator_role_id, jr_moderator_role_id, staff_channel_id, bot_log_channel_id,
                           code_submissions_log_channel_id, default_color, mod_mail_thread_channel_id)
from bot.utils.checks import check_if_tortoise_staff
from bot.utils.cooldown import CoolDown
from bot.utils.embed_handler import authored, failure, success, info, warning, info_sm

logger = logging.getLogger(__name__)


class UnsupportedFileExtension(Exception):
    pass


class UnsupportedFileEncoding(ValueError):
    pass


class StaffApplicationModal(discord.ui.Modal, title="Staff Application"):
    name_input = discord.ui.TextInput(
        label="Your Name",
        placeholder="e.g. John Doe",
        min_length=2, max_length=100,
        required=True
    )
    role_input = discord.ui.TextInput(
        label="Role Applying For",
        placeholder="e.g. Moderator, Jr Moderator, Manager",
        min_length=3, max_length=100,
        required=True
    )
    timezone_input = discord.ui.TextInput(
        label="Your Timezone",
        placeholder="e.g. UTC, EST, Asia/Kolkata",
        min_length=2, max_length=50,
        required=True
    )
    reason_input = discord.ui.Label(
        text="Tell us about yourself.",
        description="Why are you a good fit, any prior experience?",
        component=discord.ui.TextInput(
            style=discord.TextStyle.long,
            min_length=10,
            max_length=1024,
            required=True,
            placeholder="Why should we select you over other candidates?"
        )
    )

    def __init__(self, cog: "TortoiseDM"):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        await interaction.response.defer(ephemeral=True)

        formatted_submission = (
            f"**Name:** {self.name_input.value}\n"
            f"**Role:** {self.role_input.value}\n"
            f"**Timezone:** {self.timezone_input.value}\n\n"
            f"**About:**\n{self.reason_input.component.value}\n\n"
        )

        await self.cog.staff_applications_channel.send(embed=info(
            f"User {user.mention} submitted staff application:\n\n{formatted_submission}",
            self.cog.bot.user, "Staff Application", f"ID: {user.id}"
        ))

        await interaction.followup.send(
            embed=success("Staff application successfully submitted. Thank you!"),
            ephemeral=True
        )


class ModMailCloseReasonModal(discord.ui.Modal, title="Close Mod Mail with Response"):
    response_input = discord.ui.TextInput(
        label="Reason for closing",
        style=discord.TextStyle.long,
        placeholder="Type the response that will be sent to the user's DMs...",
        min_length=1,
        max_length=1024,
        required=True
    )

    def __init__(self, cog: "TortoiseDM", user_id: int):
        super().__init__()
        self.cog = cog
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        mod = interaction.user
        user_id = self.user_id
        staff_response = self.response_input.value

        channel_id = self.cog.active_mod_mails.get(user_id)
        if not channel_id:
            await interaction.response.send_message("This mod mail is no longer active.", ephemeral=True)
            return

        channel = interaction.guild.get_thread(channel_id)
        await interaction.response.defer(ephemeral=True)

        if channel:
            try:
                await interaction.followup.send(embed=info_sm("Closing modmail..."), ephemeral=True)
            except discord.HTTPException:
                pass

        await self.cog.close_mod_mail(user_id, channel, closed_by=mod, reason=staff_response, archive_thread=True)



class ModMailReasonModal(discord.ui.Modal, title="Contact Staff (Mod Mail)"):
    reason = discord.ui.Label(
        text="Reason for contacting staff",
        description="⚠️ Mod mail is strictly for reporting scams, bots or server related issues.",
        component=discord.ui.TextInput(
            style=discord.TextStyle.long,
            min_length=10,
            max_length=1024,
            required=True,
            placeholder="Please describe your issue here..."
        )
    )

    def __init__(self, cog: "TortoiseDM"):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        await interaction.response.defer(ephemeral=True)
        await self.cog.create_mod_mail(user, reason=self.reason.component.value, source="dm")


class DutyScheduleModal(discord.ui.Modal, title="Set Daily Mod Mail Schedule"):
    start_time = discord.ui.TextInput(
        label="Start Time (24h format)",
        placeholder="e.g. 09:00",
        min_length=5, max_length=5
    )
    end_time = discord.ui.TextInput(
        label="End Time (24h format)",
        placeholder="e.g. 17:00",
        min_length=5, max_length=5
    )
    timezone = discord.ui.TextInput(
        label="Your Timezone (IANA Name)",
        placeholder="e.g. Europe/London, America/New_York, Asia/Kolkata",
        min_length=4
    )

    def __init__(self, cog: "TortoiseDM"):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        tz_str = self.timezone.value.strip().replace(" ", "_")
        try:
            datetime.datetime.strptime(self.start_time.value, "%H:%M")
            datetime.datetime.strptime(self.end_time.value, "%H:%M")
            ZoneInfo(tz_str)
        except ValueError:
            await interaction.response.send_message(embed=failure("Invalid time format. Use HH:MM."), ephemeral=True)
            return
        except ZoneInfoNotFoundError:
            await interaction.response.send_message(embed=failure("Invalid timezone."), ephemeral=True)
            return

        await self.cog.duty_manager.set_schedule(
            interaction.guild.id,
            interaction.user.id,
            self.start_time.value,
            self.end_time.value,
            tz_str
        )

        await interaction.response.send_message(
            embed=success(
                f"Ping scheduled daily between {self.start_time.value} and {self.end_time.value} ({tz_str})."),
            ephemeral=True
        )


class DMInitView(discord.ui.View):
    def __init__(self, cog: "TortoiseDM", user: discord.User):
        super().__init__(timeout=300)
        self.cog = cog
        self.user = user

        for i, (emoji_id, sub_dict) in enumerate(cog._options.items()):
            if not sub_dict["check"]():
                continue

            emoji = cog.bot.app_emojis.get(emoji_id)
            if emoji is None:
                continue

            self.add_item(DMInitButton(
                emoji=emoji,
                label=sub_dict["message"],
                callback_func=sub_dict["callable"],
                row=i
            ))


class DMInitButton(discord.ui.Button):
    def __init__(self, emoji, label, callback_func, row):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            label=label,
            row=row
        )
        self.callback_func = callback_func

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        cog = interaction.client.get_cog("TortoiseDM")

        if cog.is_any_session_active(user.id):
            await interaction.response.send_message("Session already active.", ephemeral=True)
            return

        if cog.cool_down.is_on_cool_down(user.id):
            msg = f"You are on cooldown. You can retry after {cog.cool_down.retry_after(user.id)}s"
            await interaction.response.send_message(embed=failure(msg), ephemeral=True)
            return

        if self.label == "Contact staff (Mod Mail)":
            await interaction.response.send_modal(ModMailReasonModal(cog))
            if interaction.message:
                view = self.view
                view.clear_items()
                await interaction.message.edit(view=view)
            return

        if self.label == "Staff Application":
            await interaction.response.send_modal(StaffApplicationModal(cog))
            if interaction.message:
                view = self.view
                view.clear_items()
                await interaction.message.edit(view=view)
            return

        if interaction.message:
            view = self.view
            view.clear_items()
            await interaction.message.edit(view=view)

        cog.cool_down.add_to_cool_down(user.id)
        await interaction.response.defer(ephemeral=True)
        await self.callback_func(user)


class ModMailAcceptView(discord.ui.View):
    def __init__(self, cog: "TortoiseDM", user_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.user_id = user_id

    def permission_check(self, mod: discord.Member) -> bool:
        return any(role in mod.roles for role in (
            self.cog.admin_role,
            self.cog.moderator_role,
            self.cog.jr_moderator_role
        ))

    @discord.ui.button(label="Accept Mod Mail", style=discord.ButtonStyle.green, custom_id="accept_modmail_btn")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        mod = interaction.user
        user_id = self.user_id

        if not self.permission_check(mod):
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        if user_id not in self.cog.pending_mod_mails:
            await interaction.response.send_message("Mod mail is no longer pending.", ephemeral=True)
            return

        user = self.cog.bot.get_user(user_id) or await self.cog.bot.fetch_user(user_id)
        if user is None:
            await interaction.response.send_message("User not found.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        forum_channel = interaction.guild.get_channel(mod_mail_thread_channel_id)
        thread_name = f"modmail-{user.name}"

        embed = success(
            f"{mod.mention} accepted the mod mail for `{user}` (ID: {user.id}).\n\n"
            "Use the Resolve button below or archive the thread to close."
        )

        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label="Resolve with Reason", style=discord.ButtonStyle.blurple,
                                        custom_id=f"resolve_{user_id}"))

        thread_with_message = await forum_channel.create_thread(
            name=thread_name,
            content=f"{mod.mention}",
            embed=embed,
            view=view,
            reason=f"Mod Mail session for {user} (ID: {user.id})"
        )
        channel = thread_with_message.thread

        self.cog.active_mod_mails[user_id] = channel.id
        self.cog.active_mod_mail_channels[channel.id] = user_id
        self.cog.pending_mod_mails.remove(user_id)

        await self.cog.bot.modmail_manager.create_session(user_id, channel.id, interaction.message.id)

        user_embed = authored(
            f"{mod.display_name} has joined the chat and will be helping you.\n"
            "Reply here to send messages directly to the staff team.",
            author=mod
        )

        try:
            await user.send(embed=user_embed)
        except discord.Forbidden:
            await channel.send(embed=warning("The user has their DMs closed or blocked the bot."))

        self.clear_items()
        await self.cog.update_staff_embed_from_message(
            interaction.message,
            footer_append=f"☑️ Accepted by {mod.name}",
            color=discord.Color.green(),
            view=self,
            description=f"Ticket opened in {channel.mention}"
        )
        await interaction.followup.send(embed=success(f"Created ticket in {channel.mention}"), ephemeral=True)

    @discord.ui.button(label="Resolve with Reason", style=discord.ButtonStyle.blurple, custom_id="decline_reason_btn")
    async def decline_with_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.permission_check(interaction.user):
            await interaction.response.send_message("No permission.", ephemeral=True)
            return

        if self.user_id not in self.cog.pending_mod_mails:
            await interaction.response.send_message("Request is no longer pending.", ephemeral=True)
            return

        await interaction.response.send_modal(ModMailCloseReasonModal(self.cog, self.user_id))


class TortoiseDM(commands.Cog):
    mod_mail_group = app_commands.Group(name="mod_mail", description="Manage your mod mail ping schedule")

    def __init__(self, bot):
        self.bot = bot
        self._tortoise_guild = None
        self._ban_appeal_guild = None
        self._admin_role = None
        self._moderator_role = None
        self._jr_moderator_role = None
        self._mod_mail_ping_role = None
        self.cool_down = CoolDown(seconds=120)
        self.bot.loop.create_task(self.cool_down.start())

        self.active_mod_mails = {}  # dict[user_id: int] = channel_id: int
        self.active_mod_mail_channels = {}  # dict[channel_id: int] = user_id: int

        self.modmail_messages = {}
        self.pending_mod_mails = set()
        self.active_event_submissions = set()
        self.active_bug_reports = set()
        self.active_staff_applications = set()
        self._typing_active = set()

        # Keys are custom emoji IDs, sub-dict message is the message appearing in the bot DM,
        # callable is the method to call when that option is selected and check is callable that returns
        # bool whether that option is disabled or not.
        # TODO if callable errors container will not be properly updated so users will not be able to call it again
        self._options = {
            mod_mail_emoji_id: {
                "message": "Contact staff (Mod Mail)",
                "callable": self.create_mod_mail,
                "check": lambda: self.bot.tortoise_meta_cache.get("mod_mail", True)
            },
            event_emoji_id: {
                "message": "Event submission",
                "callable": self.create_event_submission,
                "check": lambda: self.bot.tortoise_meta_cache.get("event_submission", False)
            },
            staff_application_emoji_id: {
                "message": "Staff Application",
                "callable": self.create_staff_application,
                "check": lambda: self.bot.tortoise_meta_cache.get("staff_application", False)
            },
            bug_emoji_id: {
                "message": "Bug report",
                "callable": self.create_bug_report,
                "check": lambda: self.bot.tortoise_meta_cache.get("bug_report", True)
            },
        }

        self.bug_report_channel = None
        self.code_submissions_channel = None
        self.staff_applications_channel = None
        self.staff_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        # Server Utility Channels
        self.staff_channel = self.bot.get_channel(staff_channel_id)
        self.bug_report_channel = self.bot.get_channel(bot_log_channel_id)
        self.code_submissions_channel = self.bot.get_channel(code_submissions_log_channel_id)
        self.staff_applications_channel = self.bot.get_channel(bot_log_channel_id)

        active_sessions = await self.bot.modmail_manager.get_all_active()
        for session in active_sessions:
            user_id = session['user_id']
            channel_id = session['channel_id']
            msg_id = session['staff_message_id']
            self.active_mod_mails[user_id] = channel_id
            self.active_mod_mail_channels[channel_id] = user_id
            if msg_id:
                self.modmail_messages[user_id] = msg_id

        if not self.duty_automation_loop.is_running():
            self.duty_automation_loop.start()

    @property
    def tortoise_guild(self):
        if self._tortoise_guild is None:
            self._tortoise_guild = self.bot.get_guild(tortoise_guild_id)
        return self._tortoise_guild

    @property
    def ban_appeal_guild(self):
        if self._ban_appeal_guild is None:
            self._ban_appeal_guild = self.bot.get_guild(ban_appeal_server_id)
        return self._ban_appeal_guild

    @property
    def admin_role(self):
        if self._admin_role is None:
            self._admin_role = self.tortoise_guild.get_role(admin_role_id)
        return self._admin_role

    @property
    def moderator_role(self):
        if self._moderator_role is None:
            self._moderator_role = self.tortoise_guild.get_role(moderator_role_id)
        return self._moderator_role

    @property
    def jr_moderator_role(self):
        if self._jr_moderator_role is None:
            self._jr_moderator_role = self.tortoise_guild.get_role(jr_moderator_role_id)
        return self._jr_moderator_role

    @property
    def mod_mail_ping_role(self):
        if self._mod_mail_ping_role is None:
            self._mod_mail_ping_role = self.tortoise_guild.get_role(mod_mail_ping_role_id)
        return self._mod_mail_ping_role

    @tasks.loop(minutes=5)
    async def duty_automation_loop(self):
        """Background task running every minute to check schedules."""
        await self.bot.wait_until_ready()
        try:
            schedules = await self.bot.duty_manager.get_all_schedules()
            now_utc = datetime.datetime.now(datetime.timezone.utc)

            for record in schedules:
                guild = self.bot.get_guild(record["guild_id"])
                if not guild:
                    continue

                member = guild.get_member(record["user_id"])
                if not member:
                    continue

                user_tz = ZoneInfo(record["timezone"])
                local_now = now_utc.astimezone(user_tz)
                current_local_hm = local_now.strftime("%H:%M")

                start = record["start_time"]
                end = record["end_time"]

                if start < end:
                    is_duty = start <= current_local_hm < end
                else:
                    is_duty = current_local_hm >= start or current_local_hm < end

                role = self.mod_mail_ping_role
                has_role = role in member.roles

                if is_duty and not has_role:
                    await member.add_roles(role, reason="Scheduled duty started.")
                elif not is_duty and has_role:
                    await member.remove_roles(role, reason="Scheduled duty ended.")

        except Exception as e:
            logger.error(f"Error in duty loop: {e}")

    @classmethod
    def _build_embeds(cls, message: discord.Message, base_embed: discord.Embed) -> list[discord.Embed]:
        image_attachments = [
            att for att in message.attachments
            if att.content_type and att.content_type.startswith("image/")
        ]
        non_image_attachments = [
            att for att in message.attachments
            if att not in image_attachments
        ]

        if non_image_attachments:
            links = "\n".join(f"[{att.filename}]({att.url})" for att in non_image_attachments)
            base_embed.description = (
                f"{base_embed.description or ''}\n\n**Attachments:**\n{links}"
            ).strip()

        if not image_attachments:
            return [base_embed]

        embeds = []
        base_embed.set_image(url=image_attachments[0].url)
        embeds.append(base_embed)

        for att in image_attachments[1:10]:
            img_embed = discord.Embed(color=default_color)
            img_embed.set_image(url=att.url)
            embeds.append(img_embed)

        return embeds

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data.get('custom_id', '').startswith(
                'resolve_'):
            user_id = int(interaction.data['custom_id'].split('_')[1])
            await interaction.response.send_modal(ModMailCloseReasonModal(self, user_id))

    @commands.Cog.listener()
    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        if after.parent_id == mod_mail_thread_channel_id and not before.archived and after.archived:
            if after.id in self.active_mod_mail_channels:
                user_id = self.active_mod_mail_channels[after.id]

                closed_by = "Staff"
                try:
                    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.thread_update, limit=3):
                        if entry.target.id == after.id and getattr(entry.after, "archived", False):
                            closed_by = entry.user
                            break
                except (discord.Forbidden, discord.HTTPException):
                    pass

                await self.close_mod_mail(user_id, after, closed_by=closed_by, archive_thread=False)

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        if user == self.bot.user:
            return

        if isinstance(channel, discord.DMChannel):
            if user.id in self.active_mod_mails and user.id not in self._typing_active:
                self._typing_active.add(user.id)

                thread_id = self.active_mod_mails[user.id]
                thread = self.bot.get_channel(thread_id)

                if thread:
                    async with thread.typing():
                        pass

                self._typing_active.remove(user.id)

        elif isinstance(channel, discord.Thread):
            if channel.id in self.active_mod_mail_channels and channel.id not in self._typing_active:
                self._typing_active.add(channel.id)

                user_id = self.active_mod_mail_channels[channel.id]
                target_user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)

                if target_user:
                    try:
                        if not target_user.dm_channel:
                            await target_user.create_dm()
                        async with target_user.dm_channel.typing():
                            pass
                    except discord.Forbidden:
                        pass

                self._typing_active.remove(channel.id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if message.guild is None:
            if message.author.id in self.active_mod_mails:
                channel_id = self.active_mod_mails[message.author.id]
                channel = self.bot.get_channel(channel_id)

                if channel:
                    embed = discord.Embed(description=message.content, color=default_color)
                    embed.set_author(name=f"{message.author.name} (User)", icon_url=message.author.display_avatar.url)
                    embeds = self._build_embeds(message, embed)

                    await channel.send(embeds=embeds)
                return
            elif not self.is_any_session_active(message.author.id):
                await self.send_dm_options(output=message.author)
            return

        if message.channel.id in self.active_mod_mail_channels:
            user_id = self.active_mod_mail_channels[message.channel.id]
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            if user:
                embed = discord.Embed(description=message.content, color=default_color)
                embed.set_author(name=f"{message.author.display_name}",
                                 icon_url=message.author.display_avatar.url)
                embeds = self._build_embeds(message, embed)

                try:
                    await user.send(embeds=embeds)
                except discord.Forbidden:
                    await message.channel.send(embed=failure("Could not deliver message: The user closed their DMs."))
            else:
                await message.channel.send(embed=failure("User not found, they may have left Discord."))

    async def close_mod_mail(self, user_id: int, channel: discord.Thread, closed_by: Union[discord.Member, str],
                             reason: str = None, archive_thread: bool = True):
        user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)

        if user:
            try:
                msg = "Your mod mail thread has been marked as completed by staff."
                if reason:
                    msg += f"\n\n**Staff Response:**\n{reason}"
                msg += "\n\n-# If you are not satisfied with the response, please initiate a new mod mail."

                dm_embed = info(msg, self.bot.user, "Mod Mail Closed")
                dm_embed.set_footer(text="Tortoise Programming Community")
                await user.send(embed=dm_embed)
            except discord.HTTPException:
                pass

        if user_id in self.active_mod_mails:
            del self.active_mod_mails[user_id]
        if channel and channel.id in self.active_mod_mail_channels:
            del self.active_mod_mail_channels[channel.id]

        if user_id in self.pending_mod_mails:
            self.pending_mod_mails.remove(user_id)

        await self.bot.modmail_manager.close_session(user_id)

        url = channel.jump_url if channel else "Thread missing"
        await self.update_staff_embed(
            user_id,
            description=url,
            footer_append=f"🔒 Resolved by {closed_by}",
            color=discord.Color.dark_grey()
        )

        if channel:
            close_text = f"Session closed by {closed_by}."
            if reason:
                close_text += f"\n\n**Reason:** {reason}"

            await channel.send(embed=success(close_text))

            if archive_thread:
                await asyncio.sleep(5)

            try:
                await channel.edit(archived=True, locked=True, reason=f"Mod mail session closed by {closed_by}")
            except discord.NotFound:
                pass

    async def send_dm_options(self, *, output):
        if not any(sub_dict["check"]() for sub_dict in self._options.values()):
            return

        embed = discord.Embed(description="Select an option below to continue.\nUse the buttons to proceed.")
        embed.set_footer(text="Tortoise Community")

        view = DMInitView(self, output)
        await output.send(embed=embed, view=view)

    def is_any_session_active(self, user_id: int) -> bool:
        return any(
            user_id in active for active in (
                self.active_mod_mails.keys(),
                self.active_event_submissions,
                self.active_bug_reports,
                self.active_staff_applications,
            )
        )

    def _apply_staff_embed_updates(
            self,
            embed: discord.Embed,
            *,
            footer_append=None,
            description=None,
            color=None
    ):
        if description is not None:
            embed.description = description

        if footer_append:
            current = embed.footer.text if embed.footer else ""
            embed.set_footer(
                text=f"{current}\n\n{footer_append}" if current else footer_append
            )

        if color:
            embed.color = color

        return embed

    async def update_staff_embed_from_message(
            self,
            message: discord.Message,
            *,
            footer_append=None,
            description=None,
            color=None,
            view=None
    ):

        if not message.embeds: return

        embed = message.embeds[0]

        embed = self._apply_staff_embed_updates(
            embed,
            footer_append=footer_append,
            description=description,
            color=color
        )

        await message.edit(embed=embed, view=view)

    async def update_staff_embed(
            self,
            user_id: int,
            *,
            footer_append=None,
            description=None,
            color=None
    ):
        message_id = self.modmail_messages.get(user_id)
        if not message_id:
            return

        try:
            msg = await self.staff_channel.fetch_message(message_id)

            await self.update_staff_embed_from_message(
                msg,
                footer_append=footer_append,
                description=description,
                color=color
            )

        except Exception:
            pass

        if color == discord.Color.dark_grey() and user_id in self.modmail_messages:
            del self.modmail_messages[user_id]

    async def create_mod_mail(self, user: discord.User, reason: str = "No reason provided.", source: str = "dm",
                              ping=True):
        if user.id in self.pending_mod_mails or user.id in self.active_mod_mails:
            try:
                await user.send(embed=failure("You already have an active mod mail, please be patient."))
            except discord.Forbidden:
                pass
            return

        source_text = "submitted for mod mail." if source == "dm" else source
        submission_embed = authored(f"{user.name} {source_text}", author=user)
        submission_embed.add_field(name="Provided Reason", value=reason, inline=False)
        submission_embed.color = discord.Color.orange()

        view = ModMailAcceptView(self, user.id)

        msg = await self.staff_channel.send(
            self.mod_mail_ping_role.mention if ping else None,
            embed=submission_embed,
            view=view
        )
        self.modmail_messages[user.id] = msg.id
        self.pending_mod_mails.add(user.id)

        self.cool_down.add_to_cool_down(user.id)

        if source == "dm":
            embed = info("Mail is initialized and the moderators have been contacted.\n"
                         "You'll be notified once someone from the team responds.",
                         user, "ModMail Created!")
            embed.set_footer(
                text="NOTE: Response time may vary; No need to wait here."
            )
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

    async def create_event_submission(self, user: discord.User):
        user_reply = await self._get_user_reply(self.active_event_submissions, user, "Event Submission")
        if user_reply is None:
            return

        await self.code_submissions_channel.send(
            f"User `{user}` ID:{user.id} submitted code submission: "
            f"{user_reply}"
        )
        await user.send(embed=success("Event submission successfully submitted."))
        self.active_event_submissions.remove(user.id)

    async def create_staff_application(self, user: discord.User):
        pass

    async def create_bug_report(self, user: discord.User):
        user_reply = await self._get_user_reply(self.active_bug_reports, user, "Bug Report")
        if user_reply is None:
            return

        await self.bug_report_channel.send(f"User `{user}` ID:{user.id} submitted bug report: {user_reply}")
        await user.send(embed=success("Bug report successfully submitted, thank you."))
        self.active_bug_reports.remove(user.id)

    async def _get_user_reply(self, container: set, user: discord.User,
                              sub_type: str, sub_format=None) -> Union[str, None]:
        """
        Helper method to get user reply, only deals with errors.
        Uses self._wait_for method so it can get both the user message reply and text from attachment file.
        :param container: set, container holding active user sessions by having their IDs in it.
        :param user: Discord user to wait reply from
        :return: Union[str, None] string representing user reply, can be None representing invalid reply.
        """
        user_reply = await self._wait_for(container, user, sub_type, sub_format)

        if user_reply is None:
            return None

        try:
            possible_attachment = await self.get_message_txt_attachment(user_reply)
        except (UnsupportedFileExtension, UnsupportedFileEncoding) as e:
            container.remove(user.id)
            await user.send(embed=failure(f"Error: {e} , canceling."))
            return

        user_reply_content = user_reply.content if possible_attachment is None else possible_attachment

        if len(user_reply_content) < 10:
            container.remove(user.id)
            await user.send(embed=failure("Too short - seems invalid, canceling."))
            return None
        return user_reply_content

    async def _wait_for(self, container: set, user: discord.User, sub_type: str, sub_format=None) -> Union[
        discord.Message, None]:
        def check(msg):
            return msg.guild is None and msg.author == user

        container.add(user.id)
        if sub_format is not None: sub_format = "\n" + sub_format

        await user.send(embed=info(
            f"Reply with single message or link to paste service or upload a `.txt` file.\nType `cancel` to cancel right away.\n\n{'**Format: **' + sub_format if sub_format else ''}",
            user, sub_type + " Initialized", "This submission will timeout in 5 minutes.")
        )

        try:
            user_reply = await self.bot.wait_for("message", check=check, timeout=300)
        except TimeoutError:
            container.remove(user.id)
            await user.send(embed=failure("Submission timed out."))
            return

        if user_reply.content.lower() == "cancel":
            container.remove(user.id)
            await user.send(embed=success("Successfully canceled."))
            return

        return user_reply

    @classmethod
    async def get_message_txt_attachment(cls, message: discord.Message) -> Union[str, None]:
        """
        Only supports .txt file attachments and only utf-8 encoding supported.
        :param message: message object to extract attachment from.
        :return: Union[str, None]
        :raise UnsupportedFileExtension: If file type is other than .txt
        :raise UnicodeDecodeError: If decoding the file fails
        """
        try:
            attachment = message.attachments[0]
        except IndexError:
            return None

        if not attachment.filename.endswith(".txt"):
            raise UnsupportedFileExtension("Only `.txt` files supported")

        try:
            content = (await attachment.read()).decode("utf-8")
        except UnicodeDecodeError:
            raise UnsupportedFileEncoding("Unsupported file encoding, please only use utf-8")

        return content

    @classmethod
    def _get_attachments_as_urls(cls, message: discord.Message) -> str:
        if not message.attachments:
            return ""

        urls = '\n'.join(attachment.url for attachment in message.attachments)
        return f"\nAttachments:\n{urls}"

    @mod_mail_group.command(name="schedule", description="Set your daily recurring mod mail ping hours.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.check(check_if_tortoise_staff)
    async def schedule(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DutyScheduleModal(self))

    @mod_mail_group.command(name="stop", description="Remove your automatic ping schedule.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.check(check_if_tortoise_staff)
    async def stop(self, interaction: discord.Interaction):
        await self.duty_manager.remove_schedule(interaction.guild.id, interaction.user.id)

        if self.mod_mail_ping_role in interaction.user.roles:
            await interaction.user.remove_roles(self.mod_mail_ping_role, reason="Schedule deleted.")
        await interaction.response.send_message(embed=success("Your ping schedule has been deleted."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(TortoiseDM(bot))
