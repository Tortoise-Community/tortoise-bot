import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from bot import bot
from bot.constants import (
    today_i_did_channel_id, today_i_did_cooldown, today_i_did_warning
)
from bot.utils.embed_handler import warning, info_sm


class TodayIDidCog(commands.Cog):
    def __init__(self, bot: bot.Bot):
        self.bot = bot
        self.message_manager = bot.message_manager
        self.cooldown_timeout = today_i_did_cooldown
        self.last_reply_warning_timeout = today_i_did_warning
        self.last_reply_warning = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel_id = message.channel.id
        author = message.author

        if author.bot:
            return

        if channel_id != today_i_did_channel_id:
            return

        if message.reference is not None:
            await message.delete()

            now = datetime.now(timezone.utc).timestamp()

            if now - self.last_reply_warning >= self.last_reply_warning_timeout:
                warning_message = (
                    "If you want to reply to any of the messages "
                    "here please kindly create a thread. "
                    "Do not reply in messages."
                )

                await message.channel.send(embed=info_sm(warning_message))
                self.last_reply_warning = now

            return

        now = datetime.now(timezone.utc)

        last_message = await self.message_manager.get_latest_message(
            author.id,
            channel_id
        )

        if last_message is not None:
            next_allowed_at = (
                last_message["created_at"] + timedelta(seconds=self.cooldown_timeout)
            )

            if now < next_allowed_at:
                timestamp = int(next_allowed_at.timestamp())

                warning_embed = warning(
                    "You've already shared your progress recently. "
                    f"Come back <t:{timestamp}:R> :hourglass:\n\n"
                    "-# If you'd like to add more points, please edit your "
                    "existing message or create a thread instead."
                )

                try:
                    await message.delete()
                    warn_message = await message.channel.send(embed=warning_embed)

                    await asyncio.sleep(5)
                    await warn_message.delete()
                except discord.HTTPException:
                    pass

                return

        await self.message_manager.create_message(
            author.id,
            channel_id,
            message.id
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        await self.message_manager.mark_message_deleted(message.id)


async def setup(bot: bot.Bot):
    await bot.add_cog(TodayIDidCog(bot))
