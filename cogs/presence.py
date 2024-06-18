# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the 
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms 
# designated in the license will be met with swift judicial action by the author. 

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally 
# bound to the terms stipulated in the license.
import discord
from discord.ext import commands
import asyncio
from discord.ext import tasks

from config import discord_ban_register_guild_id

class presence(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.counter = 0
        self.presence_check_task.start()


    @tasks.loop(minutes=15)
    async def presence_check_task(self):
        await asyncio.sleep(10)
        if not self.presence_task.is_running():
            self.presence_task.start()
            await asyncio.sleep(10)

    
    @tasks.loop(minutes=15)  # task runs every 15 seconds
    async def presence_task(self):
        guild = await self.bot.fetch_guild(discord_ban_register_guild_id, with_counts=True)
        if guild is not None:
            online_members = guild.approximate_presence_count
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{online_members} members online'))


async def setup(bot):
    await bot.add_cog(presence(bot))
