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

from config import master_admins, netg_unban_role_ids, net_unban_role_ids, mgmt_role_ids, game_ban_log_channel_id
import discord as Discord

from helpers.embeds import interact_generate_embed
from helpers.embed import generate_embed
from helpers.webhook import send_log_to_webhook



class serverCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    servercmdsgroup = app_commands.Group(name='server', description='Server Commands')


    @servercmdsgroup.command(name='banlookup', description='Get Ban info')
    @app_commands.describe(choices='Ban Prefix')
    @app_commands.choices(choices=[
        app_commands.Choice(name="NET-", value=1),
        app_commands.Choice(name="NETG-", value=2),
    ])
    @app_commands.describe(banid='Provide the users BanID')
    async def server_banlookup(self, interaction: discord.Interaction, choices: app_commands.Choice[int], banid: int) -> None:
        requestingUser = interaction.user.id

        admin = False
        net_unban = False
        netg_unban = False
        mgmt = False

        if requestingUser in master_admins:
            admin = True

        role = Discord.utils.find(lambda r: r.id in net_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            net_unban = True

        role = Discord.utils.find(lambda r: r.id in netg_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            netg_unban = True

        role = Discord.utils.find(lambda r: r.id in mgmt_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            mgmt = True


        # Set values
        pname = 'No Matching Ban Found'
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
        reason = ''
        banreason = ''
        banexp = ''
        banstaffname = ''
        banstaffdiscordid = ''
        revoked = ''
        revoke_discordid = ''
        revoke_date = ''
        origin = ''
        revokedstatus = 'No Matching Ban Found'
        fetype = ''
        ts = ''
        tsbanexp = ''
        tsbanrev = ''

        if choices.value == 1:
            if (admin or mgmt or net_unban or netg_unban):
                try:
                    logcur = await self.bot.get_cog('Database').execute_query(
                        "SELECT pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, banreason, banexp, banstaffname, banstaffdiscordid, revoked, revoke_discordid, revoke_date, origin, time_stamp FROM banlist WHERE id=%s AND serverapiid != 0",
                        (banid,))
                    for pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, banreason, banexp, banstaffname, banstaffdiscordid, revoked, revoke_discordid, revoke_date, origin, time_stamp in logcur:
                        print(
                            f"{pname}, {steamid}, {license}, {xbl}, {ip}, {discord}, {liveid}, {hid0}, {hid1}, {hid2}, {hid3}, {hid4}, {hid5}, {hid6}, {hid7}, {hid8}, {hid9}, {banreason}, {time_stamp}, {banexp}, {banstaffname}, {banstaffdiscordid}, {revoked}, {revoke_discordid}, {revoke_date}, {origin}")
                        try:
                            dt = datetime.strptime(str(time_stamp), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            ts = f' | <t:{str(unix_timestamp)}:f>'
                        except Exception as e:
                            ts=''
                        try:
                            dt = datetime.strptime(str(banexp), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            tsbanexp = f' | <t:{str(unix_timestamp)}:f>'
                        except Exception as e:
                            tsbanexp=''
                        try:
                            dt = datetime.strptime(str(revoke_date), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            tsbanrev = f' | <t:{str(unix_timestamp)}:f>'
                        except Exception as e:
                            tsbanrev = ''

                        if revoked == '1':
                            revokedstatus = 'Unbanned'
                        else:
                            revokedstatus = 'Banned'
                    if admin:
                        await interaction.response.send_message(
                            f"Player Name: {pname} \n Steam: {steamid} \n License: {license} \n XBL: {xbl} \n IP: ||{ip}|| \n Discord: <@{discord}> | {discord} \n Live ID: {liveid} \n HID0: {hid0} \n HID1: {hid1} \n HID2: {hid2} \n HID3: {hid3} \n HID4: {hid4} \n HID5: {hid5} \n HID6: {hid6} \n HID7: {hid7} \n HID8: {hid8} \n HID9: {hid9} \n Ban ID: {choices.name}{str(banid)} \n Ban Date: {time_stamp}{ts} \n Ban Reason: {banreason} \n Ban Expiration: {banexp}{tsbanexp} \n Banning Staff Member: {banstaffname}\n Ban Staff Discord ID: {banstaffdiscordid} \n Ban Status: {revokedstatus} \n Revoking Staff Member: {revoke_discordid} \n Revoke Date: {revoke_date}{tsbanrev} \n Originating Ban ID: {choices.name}{origin}",
                            ephemeral=True)
                    elif mgmt:
                        await interaction.response.send_message(
                            f"Player Name: {pname} \n Steam: {steamid} \n License: {license} \n XBL: {xbl} \n Discord: <@{discord}> | {discord} \n Live ID: {liveid} \n HID0: {hid0} \n HID1: {hid1} \n HID2: {hid2} \n HID3: {hid3} \n HID4: {hid4} \n HID5: {hid5} \n HID6: {hid6} \n HID7: {hid7} \n HID8: {hid8} \n HID9: {hid9}  \n Ban ID: {choices.name}{str(banid)} \n Ban Date: {time_stamp}{ts} \n Ban Reason: {banreason} \n Ban Expiration: {banexp}{tsbanexp} \n Banning Staff Member: {banstaffname}\n Ban Staff Discord ID: {banstaffdiscordid} \n Ban Status: {revokedstatus} \n Revoking Staff Member: {revoke_discordid} \n Revoke Date: {revoke_date}{tsbanrev} \n Originating Ban ID: {choices.name}{origin}",
                            ephemeral=True)
                    else:
                        await interaction.response.send_message(
                            f"Player Name: {pname} \n Steam: {steamid} \n Discord: <@{discord}> | {discord} \n Additional Identifiers Redacted to Management \n Ban ID: {choices.name}{str(banid)} \n Ban Date: {time_stamp}{ts} \n Ban Reason: {banreason} \n Ban Expiration: {banexp}{tsbanexp} \n Banning Staff Member: {banstaffname}\n Ban Staff Discord ID: {banstaffdiscordid} \n Ban Status: {revokedstatus} \n Revoking Staff Member: {revoke_discordid} \n Revoke Date: {revoke_date}{tsbanrev} \n Originating Ban ID:  {choices.name}{origin}",
                            ephemeral=True)
                except Exception as e:
                    print(f"Error: {e}")
                    await interaction.response.send_message('There was an error looking up ban: ' + choices.name + str(
                        banid), ephemeral=True)
            else:
                await interaction.response.send_message(
                    'You are not Worthy of requesting Ban Information',
                    ephemeral=True)
            embed = generate_embed('Ban Lookup')
            embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
            embed.add_field(name='BanID', value=(choices.name + str(banid)), inline=False)
            embed.add_field(name='Access Approved', value=(admin or mgmt or net_unban or netg_unban), inline=False)
            embed.timestamp = interaction.created_at
            embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
            await send_log_to_webhook(self.bot, embed)

        elif choices.value == 2:
            if (admin or mgmt or netg_unban):
                try:
                    logcur = await self.bot.get_cog('Database').execute_query(
                        "SELECT pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, banreason, banexp, banstaffname, banstaffdiscordid, revoked, revoke_discordid, revoke_date, origin, time_stamp FROM banlist WHERE id=%s AND serverapiid = 0",
                        (banid,))
                    print(logcur)
                    for pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, banreason, banexp, banstaffname, banstaffdiscordid, revoked, revoke_discordid, revoke_date, origin, time_stamp in logcur:

                        try:
                            dt = datetime.strptime(str(time_stamp), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            ts = f' | <t:{str(unix_timestamp)}:f>'
                        except Exception as e:
                            ts = ''
                        try:
                            dt = datetime.strptime(str(banexp), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            tsbanexp = f' | <t:{str(unix_timestamp)}:f>'
                        except Exception as e:
                            tsbanexp = ''
                        try:
                            dt = datetime.strptime(str(revoke_date), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            tsbanrev = f' | <t:{str(unix_timestamp)}:f>'
                        except Exception as e:
                            tsbanrev = ''
                        print(
                            f"{pname}, {steamid}, {license}, {xbl}, {ip}, {discord}, {liveid}, {hid0}, {hid1}, {hid2}, {hid3}, {hid4}, {hid5}, {hid6}, {hid7}, {hid8}, {hid9}, {time_stamp}, {banreason}, {banexp}, {banstaffname}, {banstaffdiscordid}, {revoked}, {revoke_discordid}, {revoke_date}, {origin}")
                        if revoked == '1':
                            revokedstatus = 'Unbanned'
                        else:
                            revokedstatus = 'Banned'
                    if admin:
                        await interaction.response.send_message(
                            f"Player Name: {pname} \n Steam: {steamid} \n License: {license} \n XBL: {xbl} \n IP: ||{ip}|| \n Discord: <@{discord}> | {discord} \n Live ID: {liveid} \n HID0: {hid0} \n HID1: {hid1} \n HID2: {hid2} \n HID3: {hid3} \n HID4: {hid4} \n HID5: {hid5} \n HID6: {hid6} \n HID7: {hid7} \n HID8: {hid8} \n HID9: {hid9}  \n Ban ID: {choices.name}{str(banid)} \n Ban Date: {time_stamp}{ts} \n Ban Reason: {banreason} \n Ban Expiration: {banexp}{tsbanexp} \n Banning Staff Member: {banstaffname}\n Ban Staff Discord ID: {banstaffdiscordid} \n Ban Status: {revokedstatus} \n Revoking Staff Member: {revoke_discordid} \n Revoke Date: {revoke_date}{tsbanrev} \n Originating Ban ID: {choices.name}{origin}",
                            ephemeral=True)
                    elif mgmt:
                        await interaction.response.send_message(
                            f"Player Name: {pname} \n Steam: {steamid} \n License: {license} \n XBL: {xbl} \n Discord: <@{discord}> | {discord} \n Live ID: {liveid} \n HID0: {hid0} \n HID1: {hid1} \n HID2: {hid2} \n HID3: {hid3} \n HID4: {hid4} \n HID5: {hid5} \n HID6: {hid6} \n HID7: {hid7} \n HID8: {hid8} \n HID9: {hid9}  \n Ban ID: {choices.name}{str(banid)} \n Ban Date: {time_stamp}{ts} \n Ban Reason: {banreason} \n Ban Expiration: {banexp}{tsbanexp} \n Banning Staff Member: {banstaffname}\n Ban Staff Discord ID: {banstaffdiscordid} \n Ban Status: {revokedstatus} \n Revoking Staff Member: {revoke_discordid} \n Revoke Date: {revoke_date}{tsbanrev} \n Originating Ban ID: {choices.name}{origin}",
                            ephemeral=True)
                    else:
                        await interaction.response.send_message(
                            f"Player Name: {pname} \n Steam: {steamid} \n Discord: <@{discord}> | {discord} \n Additional Identifiers Redacted to Management \n Ban ID: {choices.name}{str(banid)} \n Ban Date: {time_stamp}{ts} \n Ban Reason: {banreason} \n Ban Expiration: {banexp}{tsbanexp} \n Banning Staff Member: {banstaffname}\n Ban Staff Discord ID: {banstaffdiscordid} \n Ban Status: {revokedstatus} \n Revoking Staff Member: {revoke_discordid} \n Revoke Date: {revoke_date}{tsbanrev} \n Originating Ban ID: {choices.name}{origin}",
                            ephemeral=True)
                except Exception as e:
                    print(f"Error: {e}")
                    await interaction.response.send_message('There was an error looking up ban: ' + choices.name + str(
                        banid), ephemeral=True)
            else:
                await interaction.response.send_message(
                    'You are not Worthy of requesting Ban Information',
                    ephemeral=True)
            embed = generate_embed('Ban Lookup')
            embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
            embed.add_field(name='BanID', value=(choices.name + str(banid)), inline=False)
            embed.add_field(name='Access Approved', value=(admin or mgmt or netg_unban), inline=False)
            embed.timestamp = interaction.created_at
            embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
            await send_log_to_webhook(self.bot, embed)




    @servercmdsgroup.command(name='unban', description='Unban Player from the server')
    @app_commands.describe(choices='Ban Prefix')
    @app_commands.choices(choices=[
        app_commands.Choice(name="NET-", value=1),
        app_commands.Choice(name="NETG-", value=2),
    ])
    @app_commands.describe(banid='Provide the users BanID')
    @app_commands.describe(reason='Provide the unban reason')
    async def server_unban(self, interaction: discord.Interaction, choices: app_commands.Choice[int], banid: int,
                       reason: str) -> None:
        await interaction.response.defer(thinking=True)
        requestingUser = interaction.user.id

        admin = False
        net_unban = False
        netg_unban = False
        mgmt = False

        if requestingUser in master_admins:
            admin = True

        role = Discord.utils.find(lambda r: r.id in net_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            net_unban = True

        role = Discord.utils.find(lambda r: r.id in netg_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            netg_unban = True

        role = Discord.utils.find(lambda r: r.id in mgmt_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            mgmt = True

        if choices.value == 1 or choices.value == 2:
            queryz = f"SELECT discord FROM banlist WHERE id=%s AND revoked = 0 AND banexp > CURRENT_TIMESTAMP"
            paramsz = (banid,)
            baninfoz = await self.bot.get_cog('Database').execute_query(queryz, paramsz, True)
            if baninfoz:
                discordidz = baninfoz[0]
                if discordidz == interaction.user.id:
                    await interaction.followup.send(f"You cannot revoke your own ban.")
                    # Timeout member for 28 days
                    try:
                        timeout_time = discord.utils.utcnow() + timedelta(days=28)
                        await interaction.user.timeout(timeout_time, reason=f'Attempting to revoke a server ban on themselves, {banid}')
                    except:
                        pass

                    return

        if choices.value == 1:  # NET
            if (admin or mgmt or net_unban):
                try:
                    logcur = await self.bot.get_cog('Database').execute_query(
                        f"UPDATE banlist SET revoked = 1, revoke_discordid = {interaction.user.id}, revoke_date = CURRENT_TIMESTAMP, revoke_reason = '{reason}' WHERE (id={banid} OR origin={banid}) AND revoked = 0 AND serverapiid != 0 AND banexp > CURRENT_TIMESTAMP",
                        None, True)
                    await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                                  'The Unban request has been submitted for processing on ban id: ' + choices.name + str(
                                                                                      banid)))
                except Exception as e:
                    print(f"Error: {e}")
                    await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                                  'There was an error unbanning: ' + choices.name + str(
                                                                                      banid)))
            else:
                await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                              'You are not Worthy'))
            embed = generate_embed('Unban')
            embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
            embed.add_field(name='BanID', value=(choices.name + str(banid)), inline=False)
            embed.add_field(name='Reason', value=reason, inline=False)
            embed.add_field(name='Access Approved', value=(admin or mgmt or net_unban),
                            inline=False)
            embed.timestamp = interaction.created_at
            embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
            await send_log_to_webhook(self.bot, embed)

        elif choices.value == 2:  # NETG
            if admin or mgmt or netg_unban:
                try:
                    logcur = await self.bot.get_cog('Database').execute_query(
                        f"UPDATE banlist SET revoked = 1, revoke_discordid = {interaction.user.id}, revoke_date = CURRENT_TIMESTAMP, revoke_reason='{reason}' WHERE (id={banid} OR origin={banid}) AND revoked = 0 AND serverapiid = 0 AND banexp > CURRENT_TIMESTAMP",
                        None, True)
                    await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                                  'The Unban request has been submitted for processing on ban id: ' + choices.name + str(
                                                                                      banid)))
                except Exception as e:
                    print(f"Error: {e}")
                    await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                                  'There was an error unbanning: ' + choices.name + str(
                                                                                      banid)))
            else:
                await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                              'You are not Worthy'))
            embed = generate_embed('Unban')
            embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
            embed.add_field(name='BanID', value=(choices.name + str(banid)), inline=False)
            embed.add_field(name='Reason', value=reason, inline=False)
            embed.add_field(name='Access Approved', value=(admin or mgmt, netg_unban), inline=False)
            embed.timestamp = interaction.created_at
            embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
            await send_log_to_webhook(self.bot, embed)

        else:
            await interaction.followup.send(embed=interact_generate_embed(interaction,
                                                                          'There was an error with the way you submitted the command.'))

    @servercmdsgroup.command(name='ban', description='Game Ban a User')
    @app_commands.choices(choices=[
        app_commands.Choice(name="ALL Servers", value=0),
        app_commands.Choice(name="Server 1", value=1),
        app_commands.Choice(name="Server 2", value=2),
    ])
    @app_commands.describe(member='Member you want to ban')
    @app_commands.describe(time='How many units of time to ban for')
    @app_commands.choices(timetype=[
        app_commands.Choice(name="Minutes", value=1),
        app_commands.Choice(name="Hours", value=2),
        app_commands.Choice(name="Days", value=3),
        app_commands.Choice(name="Weeks", value=4),
        app_commands.Choice(name="Months", value=5),
        app_commands.Choice(name="PERMANENT", value=6),
    ])
    @app_commands.describe(reason='Reason for the ban')
    async def server_ban(self, interaction: discord.Interaction, choices: app_commands.Choice[int],
                      member: discord.User, time: int, timetype: app_commands.Choice[int], reason: str) -> None:
        await interaction.response.defer(thinking=True)
        requestingUser = interaction.user.id
        has_permission = False

        admin = False
        net_unban = False
        netg_unban = False
        mgmt = False

        if requestingUser in master_admins:
            admin = True

        role = Discord.utils.find(lambda r: r.id in net_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            net_unban = True

        role = Discord.utils.find(lambda r: r.id in netg_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            netg_unban = True

        role = Discord.utils.find(lambda r: r.id in mgmt_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            mgmt = True

        if choices.value == 0 or timetype.value == 6:
            if (admin or mgmt):
                has_permission = True

        # Check if the member trying to assign the role has permission to do so
        assigner = interaction.user

        if choices.value == 0:
            banreason = f'You have been banned from all servers for {time} {timetype.name} for {reason} by {assigner.name}'
        else:
            banreason = f'You have been banned from {choices.name} for {time} {timetype.name} for {reason} by {assigner.name}'

        if (admin or mgmt or net_unban or netg_unban):
            has_permission = True
        try:
            # Check if the role being assigned is higher than the user's highest role
            highest_role = assigner.top_role
            member_highest_role = member.top_role
            if member_highest_role.position >= highest_role.position:
                has_permission = False
                await interaction.followup.send(embed=interact_generate_embed(interaction, 'Game Ban',
                                                                              'You cannot ban someone with a equal or higher role than your highest role.'))
                return
        except:
            pass

        # has_permission = await has_permission(assigner, role)
        embed = generate_embed('Game Ban')
        embed.add_field(name='Guild', value=interaction.guild, inline=False)
        embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
        embed.add_field(name='Target', value=member.mention, inline=True)
        embed.add_field(name='Reason', value=banreason, inline=True)
        embed.add_field(name='Duration', value=str(time) + ' ' + str(timetype.name), inline=True)
        embed.add_field(name='Access Approved', value=has_permission, inline=False)
        embed.timestamp = interaction.created_at
        embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
        await send_log_to_webhook(self.bot, embed)

        if not has_permission:
            await interaction.followup.send(embed=interact_generate_embed(interaction, 'Game Ban',
                                                                          'You are not Worthy of completing this action.'))
            return

        from datetime import datetime, timedelta
        import requests

        id = ''
        serverapiid = ''
        pname = ''
        steamid = ''
        license = ''
        xbl = ''
        ip = ''
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

        # Second query
        query = "SELECT id, serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, time_stamp FROM idents WHERE discord = %s ORDER BY id DESC LIMIT 1"
        params = (str(member.id),)
        result = await self.bot.get_cog('Database').execute_query_one(query, params)
        if result:
            id, serverapiid, pname, steamid, license, xbl, ip, discordid, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, time_stamp = result


        if choices.value == 0:
            sdesc = 'ALL Servers'
        else:
            sdesc = choices.name

        keys: dict[int, str] = {
            1: "INSERT INTO banlist (serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banexp, banreason, banstaffname, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ADDDATE(CURRENT_TIMESTAMP, INTERVAL %s MINUTE), %s, %s, %s);",
            2: "INSERT INTO banlist (serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banexp, banreason, banstaffname, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ADDDATE(CURRENT_TIMESTAMP, INTERVAL %s HOUR), %s, %s, %s);",
            3: "INSERT INTO banlist (serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banexp, banreason, banstaffname, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ADDDATE(CURRENT_TIMESTAMP, INTERVAL %s DAY), %s, %s, %s);",
            4: "INSERT INTO banlist (serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banexp, banreason, banstaffname, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ADDDATE(CURRENT_TIMESTAMP, INTERVAL %s WEEK), %s, %s, %s);",
            5: "INSERT INTO banlist (serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banexp, banreason, banstaffname, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ADDDATE(CURRENT_TIMESTAMP, INTERVAL %s MONTH), %s, %s, %s);",
            6: "INSERT INTO banlist (serverapiid, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem, banreason, banstaffname, banstaffdiscordid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        }
        if timetype.value == 6:
            params = (
            choices.value, member.name, steamid, license, xbl, ip, str(member.id), liveid, hid0, hid1, hid2, hid3, hid4,
            hid5, hid6, hid7, hid8, hid9, fivem, banreason, interaction.user.name, str(interaction.user.id))
        else:
            params = (
            choices.value, member.name, steamid, license, xbl, ip, str(member.id), liveid, hid0, hid1, hid2, hid3, hid4,
            hid5, hid6, hid7, hid8, hid9, fivem, time, banreason, interaction.user.name, str(interaction.user.id))

        result = await self.bot.get_cog('Database').execute_query_one(keys.get(timetype.value, None), params, True)

        query = "SELECT id FROM banlist WHERE discord = %s ORDER BY id DESC LIMIT 1;"
        params = (str(member.id),)
        result = await self.bot.get_cog('Database').execute_query_one(query, params, True)

        try:
            if choices.value == 0:
                banidprint = f'NETG-{str(result[0])}'
            else:
                banidprint = f'NET-{str(result[0])}'
        except:
            banidprint = 'Error Retrieving Ban ID'
        await interaction.followup.send(embed=interact_generate_embed(interaction, 'Game Ban',
                                                                      f'You have successfully banned {member.mention} from {choices.name} for {time} {timetype.name} for {reason}\n\n Ban ID: {banidprint}'))

        embed = discord.Embed(title=f"{sdesc} Ban Log", color=0x00ff00)
        embed.add_field(name='Player Name', value=pname, inline=True)
        embed.add_field(name='Discord', value=member.mention, inline=True)
        embed.add_field(name='Discord ID', value=f'```{member.id}```', inline=True)
        embed.add_field(name='Server', value=choices.name, inline=False)
        embed.add_field(name='Ban Reason', value=f"```{reason}```", inline=False)
        embed.add_field(name='Ban Length', value=str(time) + ' ' + str(timetype.name), inline=False)
        embed.add_field(name='Ban ID', value=banidprint, inline=False)
        embed.add_field(name='Performed By', value=assigner.mention, inline=False)
        embed.timestamp = interaction.created_at
        embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
        await self.bot.get_cog("messageSendQueue").send_message(type='channel', userorchannelid=game_ban_log_channel_id, content=f'<@{interaction.user.id}>', embed=embed)

    @servercmdsgroup.command(name='banhistory', description='Get Ban History')
    @app_commands.describe(user='User you want to lookup ban history for')
    async def server_banhistory(self, interaction: discord.Interaction, user: discord.User) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        has_permission = False
        requestingUser = interaction.user.id

        admin = False
        net_unban = False
        netg_unban = False
        mgmt = False

        if requestingUser in master_admins:
            admin = True
            has_permission = True

        role = Discord.utils.find(lambda r: r.id in net_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            net_unban = True
            has_permission = True

        role = Discord.utils.find(lambda r: r.id in netg_unban_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            netg_unban = True
            has_permission = True

        role = Discord.utils.find(lambda r: r.id in mgmt_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            mgmt = True
            has_permission = True

        if has_permission:
            query = """SELECT serverapiid, id, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, banreason, banexp, banstaffname, banstaffdiscordid, revoked, revoke_discordid, revoke_date, origin, time_stamp 
            FROM banlist 
            WHERE origin IS NULL AND discord = %s
            """
            logcur = await self.bot.get_cog('Database').execute_query(query, (user.id,))
            if logcur:
                for serverapiid, id, pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, banreason, banexp, banstaffname, banstaffdiscordid, revoked, revoke_discordid, revoke_date, origin, time_stamp in logcur:
                    if serverapiid == 0:
                        banid = f'NETG-{str(id)}'
                        servername = 'ALL Servers'
                    else:
                        banid = f'NET-{str(id)}'
                        servername = f'Server {str(serverapiid)}'
                    if revoked == '1':
                        revokedstatus = 'Unbanned'
                    else:
                        revokedstatus = 'Banned'
                    try:
                        dt = datetime.strptime(str(time_stamp), '%Y-%m-%d %H:%M:%S')
                        unix_timestamp = int(dt.timestamp())
                        ts = f'<t:{str(unix_timestamp)}:f>'
                    except Exception as e:
                        ts = ''
                    try:
                        dt = datetime.strptime(str(banexp), '%Y-%m-%d %H:%M:%S')
                        unix_timestamp = int(dt.timestamp())
                        tsbanexp = f'<t:{str(unix_timestamp)}:f>'
                    except Exception as e:
                        tsbanexp = ''
                    try:
                        dt = datetime.strptime(str(revoke_date), '%Y-%m-%d %H:%M:%S')
                        unix_timestamp = int(dt.timestamp())
                        tsbanrev = f'<t:{str(unix_timestamp)}:f>'
                    except Exception as e:
                        tsbanrev = ''
                    embed = generate_embed(title=f"{banid} Ban Log")
                    embed.color = 0x00ff00
                    embed.add_field(name='Player Name', value=pname, inline=True)
                    embed.add_field(name='Discord', value=user.mention, inline=True)
                    embed.add_field(name='Steam', value=steamid, inline=True)
                    embed.add_field(name='Server', value=servername, inline=False)
                    embed.add_field(name='Ban Time', value=f'{ts}| {time_stamp}UTC', inline=False)
                    embed.add_field(name='Ban Reason', value=banreason, inline=False)
                    embed.add_field(name='Ban Expiration', value=f'{tsbanexp}| {banexp}UTC', inline=False)
                    embed.add_field(name='Ban ID', value=banid, inline=False)
                    embed.add_field(name='Performed By', value=banstaffname, inline=False)
                    embed.add_field(name='Status', value=revokedstatus, inline=False)
                    embed.add_field(name='Revoked By', value=f'<@{revoke_discordid}>', inline=False)
                    embed.add_field(name='Revoked Date', value=f'{tsbanrev}| {revoke_date}UTC', inline=False)

                    await interaction.followup.send(embed=embed, ephemeral=True)
                await interaction.followup.send(embed=interact_generate_embed(interaction, 'Game Ban History', "Completed"), ephemeral=True)
            await interaction.followup.send(embed=interact_generate_embed(interaction, 'Game Ban History', 'No Found'), ephemeral=True)
        else:
            await interaction.followup.send(embed=interact_generate_embed(interaction, 'Game Ban History', 'You are not Worthy of completing this action.'))

        embed = generate_embed('Ban History Requested')
        embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
        embed.add_field(name='Target', value=user.mention, inline=True)
        embed.add_field(name='Access Approved', value=has_permission, inline=False)
        embed.timestamp = interaction.created_at
        embed.set_footer(text='Created by: discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
        await send_log_to_webhook(self.bot, embed)



async def setup(bot):
    await bot.add_cog(serverCommands(bot))
