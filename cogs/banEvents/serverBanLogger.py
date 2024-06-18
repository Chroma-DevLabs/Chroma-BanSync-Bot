# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms
# designated in the license will be met with swift judicial action by the author.

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally
# bound to the terms stipulated in the license.
import discord
from discord import AuditLogEntry, AuditLogAction, RawMemberRemoveEvent
from discord import RawMemberRemoveEvent
from discord.ext import commands
from discord import app_commands

import random
import sys
import datetime
import config

from config import game_ban_log_channel_id

from discord.ext.commands import Bot
from discord.ext import tasks
import datetime
from datetime import datetime, timedelta
import time

from discord.ext import commands
import asyncio

banembeddescription = """For each ban in which you are pinged, ensure that you do the following:

- Right click on the message and click `Create Thread`
- Provide your proof of the ban via clip or screenshot of the incident
- Provide a brief description if your in game ban reason wasn't enough"""

class serverBanLogger(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.banLoggerLoopcheck_task.start()

    @tasks.loop(minutes=5)
    async def banLoggerLoopcheck_task(self):
        await asyncio.sleep(10)
        if not self.banLoggerLoop.is_running():
            await asyncio.sleep(10)
            self.banLoggerLoop.start()


    @tasks.loop(seconds=15)  # task runs every 15 seconds
    async def banLoggerLoop(self):
        query = """SELECT id, serverapiid, pname, pid, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, time_stamp, fivem, banreason, banexp, banstaffdiscordid
        FROM banlist
        WHERE webhook = '0'
        AND origin IS NULL
        AND banstaffdiscordid IS NOT NULL 
        AND banstaffapisessionid IS NOT NULL
        """
        results = await self.bot.get_cog('Database').execute_query(query)
        if results:
            for banresult in results:
                id, serverapiid, pname, pid, steamid, license, xbl, ip, discordid, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, time_stamp, fivem, banreason, banexp, banstaffdiscordid = banresult
                ts = ''
                expts = ''
                if serverapiid == 0:
                    sdesc = 'All Servers'
                    banidprint = f'NETG-{str(id)}'
                else:
                    sdesc = f'Server {str(serverapiid)}'
                    banidprint = f'NET-{str(id)}'
                # convert banexp of datetime to
                try:
                    dt = datetime.strptime(str(time_stamp), '%Y-%m-%d %H:%M:%S')
                    unix_timestamp = int(dt.timestamp())
                    ts = f'{dt} UTC | <t:{str(unix_timestamp)}:f> | <t:{str(unix_timestamp)}:R>'
                except Exception as e:
                    ts = ''
                try:
                    expdt = datetime.strptime(str(banexp), '%Y-%m-%d %H:%M:%S')
                    expunix_timestamp = int(expdt.timestamp())
                    expts = f'{expdt} UTC | <t:{str(expunix_timestamp)}:f> | <t:{str(expunix_timestamp)}:R>'
                except Exception as e:
                    expts = ''

                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Approved", style=discord.ButtonStyle.green, custom_id=f"serverbanapproved:{id}:{banstaffdiscordid}"))
                view.add_item(discord.ui.Button(label="Revoke", style=discord.ButtonStyle.red, custom_id=f"serverbanrevoke:{id}:{banstaffdiscordid}"))
                view.add_item(discord.ui.Button(label="Remind for Ban Proof", style=discord.ButtonStyle.blurple, custom_id=f"serverbanremind:{id}:{banstaffdiscordid}"))

                embed = discord.Embed(title=f"{sdesc} Ban Log", description=banembeddescription, color=0xff0000)
                embed.add_field(name='Player Name', value=pname, inline=True)
                embed.add_field(name='Player ID', value=f'{pid}', inline=True)
                if discordid == '':
                    pass
                else:
                    embed.add_field(name='Discord', value=f'<@{discordid}>', inline=True)
                    embed.add_field(name='Discord ID', value=f'```{discordid}```', inline=True)
                embed.add_field(name='Server', value=sdesc, inline=False)
                embed.add_field(name='Ban Reason', value=f"```{banreason}```", inline=False)
                embed.add_field(name='Ban Expiration', value=expts, inline=False)
                embed.add_field(name='Ban ID', value=banidprint, inline=False)
                embed.add_field(name='Performed By', value=f'<@{banstaffdiscordid}>', inline=False)
                embed.add_field(name='Performed at', value=ts, inline=False)
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text='\u200b', icon_url=self.bot.user.avatar.url)
                # await send_log_to_webhook_pass(self.bot, embed, banlogswebhook, f'<@{interaction.user.id}>')
                await self.bot.get_cog("WebhookLogger").send_log_to_webhook(embed=embed)
                await self.bot.get_cog("messageSendQueue").send_message(type='channel',
                                                                        userorchannelid=game_ban_log_channel_id,
                                                                        content=f'<@{banstaffdiscordid}>',
                                                                        embed=embed,
                                                                        view=view
                                                                        )
                query = """UPDATE banlist
                SET webhook = 1
                WHERE id = %s
                """
                parameters = (id,)
                result = await self.bot.get_cog('Database').execute_query(query, parameters, True)

async def setup(bot):
    await bot.add_cog(serverBanLogger(bot))

