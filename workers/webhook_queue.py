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
from config import webhook as config_webhook_url


class WebhookLogger(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.bot.loop.create_task(self.process_queue())

    async def send_log_to_webhook(self, embed: discord.Embed, content: str = None, log_webhook: str = config_webhook_url) -> None:
        await self.queue.put((embed, content, log_webhook))

    async def process_queue(self):
        while True:
            embed, content, log_webhook = await self.queue.get()
            async with aiohttp.ClientSession() as session:
                webhook: discord.Webhook = discord.Webhook.from_url(log_webhook, session=session)
                try:
                    if content is not None:
                        await webhook.send(content=content, embed=embed, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
                    else:
                        await webhook.send(embed=embed, username=self.bot.user.display_name, avatar_url=self.bot.user.avatar.url)
                except Exception as e:
                    print(f"An error occurred: {e}")
                    await self.queue.put((embed, content, log_webhook))  # Put the message back in the queue to try again later
            await asyncio.sleep(1)  # Sleep for a short time to prevent hitting rate limits


async def setup(bot):
    await bot.add_cog(WebhookLogger(bot))



# await self.bot.get_cog("WebhookLogger").send_log_to_webhook(embed=embed, content='<@699439754462363718>', log_webhook=[Option url])
