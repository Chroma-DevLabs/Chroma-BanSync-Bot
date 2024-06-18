# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the 
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms 
# designated in the license will be met with swift judicial action by the author. 

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally 
# bound to the terms stipulated in the license.
import asyncio
import aiohttp
import discord
from discord.ext import commands


class messageSendQueue(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.msgqueue = asyncio.Queue()
        self.bot.loop.create_task(self.msgsendprocess_queue())

    async def send_message(self, type: str, userorchannelid: int, content: str = None, embed: discord.Embed = None, view: discord.ui.View = None) -> None:
        await self.msgqueue.put((type, userorchannelid, content, embed, view))

    async def msgsendprocess_queue(self):
        while True:
            type, userorchannelid, content, embed, view = await self.msgqueue.get()

            try:
                if type == 'user':
                    user = await self.bot.fetch_user(userorchannelid)
                    await user.send(content=content, embed=embed, view=view)
                elif type == 'channel':
                    channel = self.bot.get_channel(userorchannelid)
                    await channel.send(content=content, embed=embed, view=view)
            except Exception as e:
                print(f"Error sending message: {type}({str(userorchannelid)})| {e}")

            await asyncio.sleep(1)  # Sleep for a short time to prevent hitting rate limits


async def setup(bot):
    await bot.add_cog(messageSendQueue(bot))




# await self.bot.get_cog("messageSendQueue").send_message(type='user', userorchannelid=interaction.user.id, content='test', embed=embed, view=view)