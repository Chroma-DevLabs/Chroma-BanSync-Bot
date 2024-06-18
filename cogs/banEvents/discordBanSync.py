# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the 
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms 
# designated in the license will be met with swift judicial action by the author. 

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally 
# bound to the terms stipulated in the license.
from typing import Optional

import discord
from discord.ext import commands

from discord import app_commands
from typing import List
from discord.ext.commands import Bot
from discord.ext import tasks
import datetime
from datetime import datetime, timedelta
import time

import sys

import discord as Discord
from config import discord_ban_register_guild_id
class discordBanSync(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='syncbanstoserver', description='Sync bans to the server')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    @app_commands.guilds(discord_ban_register_guild_id)
    async def syncbanstoserver(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.followup.send("Syncing bans to the server...", ephemeral=True)
        guild = interaction.guild
        count = 0
        totalbanscount = 0
        async for ban in guild.bans(limit=None):
            totalbanscount += 1
        embedOne = discord.Embed(title="Sync All Bans", description=f"**{guild.name} Total bans:** {totalbanscount}")
        intmsg = await interaction.channel.send(embed=embedOne)
        async for ban in guild.bans(limit=None):
            count += 1
            # Check if there is already an active ban in banlist table where is_active = 1
            query = "SELECT id FROM banlist WHERE discord=%s AND revoked = 0 AND banexp > CURRENT_TIMESTAMP"
            values = (ban.user.id,)
            results = await self.bot.get_cog('Database').execute_query(query, values)
            if results:
                pass
            else:
                # If there is no active ban, insert a new ban
                banUserID = ban.user.id
                banReason = ban.reason
                banStaff = self.bot.user.id
                await self.ban_player(banUserID, banReason, banStaff)
            if count % 10 == 0:
                embed = discord.Embed(title="Sync All Bans", description=f"**{guild.name} Total bans:** {totalbanscount} **Completed Ban Syncs:** {count}")
                await intmsg.edit(embed=embed)
        embed = discord.Embed(title="Sync All Bans", description=f"**{guild.name} Total bans:** {totalbanscount} **Current ban:** {count}")
        await intmsg.edit(embed=embed)




    async def ban_player(self, discordid: int, banreason: str, staffmemberid: int):
        pname = ''
        steamid = ''
        license = ''
        xbl = ''
        ip = ''
        discord = ''
        liveid = ''
        hid0 = ''
        hid1 = ''
        hid2 = ''
        hid3 = ''
        hid4 = ''
        hid5 = ''
        hid6 = ''
        hid7 = ''
        hid8 = ''
        hid9 = ''
        time_stamp = ''
        fivem = ''

        r = await self.bot.get_cog('Database').execute_query_one(
            "SELECT pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, time_stamp, fivem FROM idents WHERE discord=%s ORDER BY time_stamp DESC LIMIT 1",
            (discordid,))
        if r:
            pname = r[0]
            steamid = r[1]
            license = r[2]
            xbl = r[3]
            ip = r[4]
            discord = r[5]
            liveid = r[6]
            hid0 = r[7]
            hid1 = r[8]
            hid2 = r[9]
            hid3 = r[10]
            hid4 = r[11]
            hid5 = r[12]
            hid6 = r[13]
            hid7 = r[14]
            hid8 = r[15]
            hid9 = r[16]
            time_stamp = r[17]
            fivem = r[18]

        # insert information
        result = await self.bot.get_cog('Database').execute_query_one(
            "INSERT INTO banlist (pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banreason, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (pname, steamid, license, xbl, ip, discordid, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8,
             hid9, fivem, banreason, staffmemberid), True)


async def setup(bot):
    await bot.add_cog(discordBanSync(bot))
