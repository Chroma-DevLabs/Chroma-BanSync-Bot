# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms
# designated in the license will be met with swift judicial action by the author.

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally
# bound to the terms stipulated in the license.
import discord
import discord as discordpkg
from discord import AuditLogEntry, AuditLogAction, RawMemberRemoveEvent
from discord import RawMemberRemoveEvent
from discord.ext import commands
from discord import app_commands
import discord as dddiscord
import random
import sys
import datetime

from helpers.embed import generate_embed

from discord.ext.commands import Bot
from discord.ext import tasks
import datetime
from datetime import datetime, timedelta
import time

from discord.ext import commands
import asyncio
import re
import discord as _discord

from config import discord_ban_log_channel_id, discord_ban_register_guild_id, server_api_ids

banembeddescription = """Ensure that you do the following for this action:

- Right click on the message and click Create Thread
- Provide your proof supporting the action via clip or screenshot of the incident
- Provide a brief description for the reason for your action if your action reason wasn't enough"""

class discordOnBanProcessing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        changes = entry.changes
        if entry.action == AuditLogAction.kick:
            useral = entry.user

            if entry.guild.id == discord_ban_register_guild_id:

                staffmemberid = 'Unknown Staff Member'
                try:
                    # Use regular expressions to find the substring between parentheses
                    match = re.search(r'\((.*?)\)', entry.reason)

                    # Extract the matched group if found, else None
                    staffmemberid = f'{match.group(1)}' if match else None
                    if staffmemberid is None:
                        staffmemberid = str(entry.user.id)
                except:
                    pass

                targetuser = await self.bot.fetch_user(entry.target.id)
                targetusername = 'Unknown User'
                if targetuser is not None:
                    targetusername = targetuser.name


                embed = generate_embed(title='Discord Kick', description=banembeddescription)
                embed.color = 0xffee00
                embed.add_field(name='Member', value='<@' + str(entry.target.id) + '>', inline=True)
                embed.add_field(name='Member ID', value=f'```{entry.target.id}```', inline=True)
                embed.add_field(name='Server', value=entry.guild, inline=True)
                embed.add_field(name='Staff Member', value='<@' + staffmemberid + '>', inline=False)
                banreason = f'{targetusername} | {entry.target.id} has been kicked from {entry.guild} | Reason: {entry.reason}'
                embed.add_field(name='Reason', value=f'```{banreason}```', inline=False)

                embed.timestamp = datetime.now(self.bot.timezone)
                embed.set_footer(text='\u200b', icon_url=self.bot.user.avatar.url)
                await self.bot.get_cog("WebhookLogger").send_log_to_webhook(embed=embed)

                view = dddiscord.ui.View()
                view.add_item(dddiscord.ui.Button(label="Approved", style=dddiscord.ButtonStyle.green,
                                                  custom_id=f"discordkickapproved:{str(entry.target.id)}:{staffmemberid}"))
                view.add_item(dddiscord.ui.Button(label="Denied", style=dddiscord.ButtonStyle.red,
                                                  custom_id=f"discordkickdenied:{str(entry.target.id)}:{staffmemberid}"))
                view.add_item(dddiscord.ui.Button(label="Remind for Kick Proof", style=dddiscord.ButtonStyle.blurple,
                                                  custom_id=f"discordkickremind:{str(entry.target.id)}:{staffmemberid}"))

                await self.bot.get_cog("messageSendQueue").send_message(type='channel',
                                                                        userorchannelid=discord_ban_log_channel_id,
                                                                        content=f'<@{staffmemberid}>',
                                                                        embed=embed,
                                                                        view=view
                                                                        )

                discordid = entry.target.id

                for i in server_api_ids:
                    result = await self.bot.get_cog('Database').execute_query_one(
                        "INSERT INTO serveractionqueue (serverapiid, paction, v1, v2, requested_by) VALUES (%s, %s, %s, %s, %s)",
                        (str(i), 'dropplayer', discordid,
                         'You have been Kicked \n Reason: ' + entry.reason,
                         f'{entry.guild}'), True)


        elif entry.action == AuditLogAction.ban:
            useral = entry.user

            if entry.guild.id == discord_ban_register_guild_id:

                staffmemberid = str(entry.user.id)
                try:
                    # Use regular expressions to find the substring between parentheses
                    match = re.search(r'\((.*?)\)', entry.reason)

                    # Extract the matched group if found, else None
                    staffmemberid = f'{match.group(1)}' if match else None
                    if staffmemberid is None:
                        staffmemberid = str(entry.user.id)
                except:
                    staffmemberid = str(entry.user.id)

                targetuser = await self.bot.fetch_user(entry.target.id)
                targetusername = 'Unknown User'
                if targetuser is not None:
                    targetusername = targetuser.name

                embed = generate_embed(title='Discord Ban', description=banembeddescription)
                embed.color = 0xff0000
                embed.add_field(name='Member', value='<@' + str(entry.target.id) + '>', inline=True)
                embed.add_field(name='Member ID', value=f'```{entry.target.id}```', inline=True)
                embed.add_field(name='Server', value=entry.guild, inline=True)
                embed.add_field(name='Staff Member', value='<@' + staffmemberid + '>', inline=False)
                banreason = f'{targetusername} | {entry.target.id} has been banned from {entry.guild} | Reason: {entry.reason}'
                embed.add_field(name='Reason', value=f'```{banreason}```', inline=False)

                embed.timestamp = datetime.now(self.bot.timezone)
                embed.set_footer(text='\u200b', icon_url=self.bot.user.avatar.url)
                # await send_log_to_webhook(self.bot, embed)
                await self.bot.get_cog("WebhookLogger").send_log_to_webhook(embed=embed)

                view = dddiscord.ui.View()
                view.add_item(dddiscord.ui.Button(label="Approved", style=dddiscord.ButtonStyle.green,
                                                custom_id=f"discordbanapproved:{str(entry.target.id)}:{staffmemberid}", row=0))
                view.add_item(dddiscord.ui.Button(label="Review Needed", style=dddiscord.ButtonStyle.red,
                                                  custom_id=f"discordbanreviewneeded:{str(entry.target.id)}:{staffmemberid}", row=0))
                view.add_item(dddiscord.ui.Button(label="Remind for Ban Proof", style=dddiscord.ButtonStyle.blurple,
                                                custom_id=f"discordbanremind:{str(entry.target.id)}:{staffmemberid}", row=0))
                view.add_item(dddiscord.ui.Button(label="UnGlobalban", style=dddiscord.ButtonStyle.red,
                                                custom_id=f"discordbanrevoke:{str(entry.target.id)}:{staffmemberid}", row=1))

                await self.bot.get_cog("messageSendQueue").send_message(type='channel',
                                                                        userorchannelid=discord_ban_log_channel_id,
                                                                        content=f'<@{staffmemberid}>',
                                                                        embed=embed,
                                                                        view=view
                                                                        )

                print(entry.target)
                print(entry.target.id)
                print(entry.guild)
                discordid = entry.target.id

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
                    (pname, steamid, license, xbl, ip, discordid, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banreason, staffmemberid), True)

                # drop player
                for i in server_api_ids:
                    result = await self.bot.get_cog('Database').execute_query_one(
                        "INSERT INTO serveractionqueue (serverapiid, paction, v1, v2, requested_by) VALUES (%s, %s, %s, %s, %s)",
                        (str(i), 'dropplayer', discordid,
                         'You have been Banned \n Reason: ' + entry.reason,
                         f'{entry.guild}'), True)



        elif entry.action == AuditLogAction.unban:
            reason = entry.reason
            guild = entry.guild
            user = entry.target
            if guild.id == discord_ban_register_guild_id:

                embed = generate_embed('Member Unban')
                embed.add_field(name='Member', value='<@' + str(user.id) + '>', inline=False)
                embed.add_field(name='Member ID', value=user.id, inline=False)
                embed.add_field(name='Server', value=guild, inline=False)
                embed.timestamp = datetime.now(self.bot.timezone)
                embed.set_footer(text='\u200b', icon_url=self.bot.user.avatar.url)
                await self.bot.get_cog("WebhookLogger").send_log_to_webhook(embed=embed)


                discordid = user.id

                # update information

                result = await self.bot.get_cog('Database').execute_query_one(
                    "UPDATE banlist SET revoked=1, revoke_reason = %s, revoke_date = CURRENT_TIMESTAMP WHERE discord=%s AND revoked = 0 AND banexp > CURRENT_TIMESTAMP",
                    (reason, str(discordid)), True)





async def setup(bot):
    await bot.add_cog(discordOnBanProcessing(bot))

