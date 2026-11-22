import asyncio
import discord
from discord import ChannelType
from discord.ext import commands
from bot.constants import job_board_channel_id, dev_board_channel_id
from bot.utils.embed_handler import simple_embed

embed = simple_embed(
    (
        "# :warning: Attention!\n"
        "When posting or replying to others please stick to the **Community Guidelines**.\n"
        "### **For OP:**\n"
        "Please keep your content appropriate, relevant and respectful. "
        "Ensure your posts comply with community rules and guidelines.\n"
        "### **See Something Suspicious?**\n"
        "If you see a message that looks suspicious, or is a scam, or breaks our rules in any way, "
        "please report it to the staff team instead of interacting with it.\n"
    ),
    ""
)


class MarketplaceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_warning(self, thread_id):
        await asyncio.sleep(4)
        thread = await self.bot.fetch_channel(thread_id)
        await thread.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        forum_channel = thread.parent

        if forum_channel and forum_channel.type == ChannelType.forum:
            if forum_channel.id == job_board_channel_id:
                await self.send_warning(thread.id)

            if forum_channel.id == dev_board_channel_id:
                await self.send_warning(thread.id)


async def setup(bot):
    await bot.add_cog(MarketplaceCog(bot))
