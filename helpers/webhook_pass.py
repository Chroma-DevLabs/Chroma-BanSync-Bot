# CC BY-NC-ND 4.0 2022 Mauro M. - webhook in project calirp-calihub 

# The aforementioned code and documents are protected and released to the public under the Creative Commons 
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the 
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms 
# designated in the license will be met with swift judicial action by the author. 

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally 
# bound to the terms stipulated in the license.
import aiohttp
import discord

from config import webhook as webhook_url
from discord.ext import commands


async def send_log_to_webhook(bot: discord.ext.commands.Bot, embed: discord.Embed, log_webhook: str, contentstr: str = '') -> None:
    async with aiohttp.ClientSession() as session:
        webhook: discord.Webhook = discord.Webhook.from_url(log_webhook, session=session)
        if contentstr == '':
            await webhook.send(embed=embed, username=bot.user.display_name, avatar_url=bot.user.avatar.url)
        else:
            await webhook.send(content=contentstr, embed=embed, username=bot.user.display_name, avatar_url=bot.user.avatar.url)

