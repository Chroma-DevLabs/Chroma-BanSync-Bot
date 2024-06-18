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
import requests



import discord as Discord

from helpers.embeds import interact_generate_embed
from helpers.embed import generate_embed
from helpers.webhook import send_log_to_webhook
from config import master_admins, net_unban_role_ids, netg_unban_role_ids, mgmt_role_ids

class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    userinfocmds = app_commands.Group(name='user', description='User Information')

    async def get_recent_disconnect_time(self, checkedmember):
        query = f"""
            SELECT disconnectt
            FROM connectdisconnect
            WHERE discord = '{checkedmember.id}' AND serverapiid < 4
            ORDER BY disconnectt DESC
            LIMIT 1
        """

        try:
            return await self.bot.get_cog('Database').execute_query_one(query)
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def get_time_format(self, total_seconds):
        """Format seconds into hours, minutes, and seconds."""
        if total_seconds is not None:
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return f"{hours}h {minutes}m"
        else:
            return "0h 0m"


    @userinfocmds.command(name='info', description='Get a users info')
    @app_commands.describe(user='The user you want to lookup')
    async def user_info(self, interaction: discord.Interaction, user: discord.User) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        member = interaction.guild.get_member(user.id)
        if not member:
            try:
                member = await interaction.guild.fetch_member(user.id)
            except discord.NotFound:
                pass

        checkedmember = member

        # Determine if the user is banned
        try:
            ban_info = await interaction.guild.fetch_ban(user)
            ban_reason = ban_info.reason
        except discord.NotFound:
            ban_reason = "Not Banned"

        # Get the user's creation date
        created_at = user.created_at.strftime("%b %d, %Y %H:%M:%S")

        # Build the main embed
        embed = discord.Embed(
            title=f"{user.name}'s Info",
            color=discord.Color.blurple()
        )

        embed.add_field(name="Name", value=user.name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Created at", value=created_at, inline=True)
        embed.add_field(name="Banned?", value=ban_reason, inline=True)

        if member:

            # Determine the user's status
            if checkedmember.status == discord.Status.online:
                status = "Online"
            elif checkedmember.status == discord.Status.idle:
                status = "Idle"
            elif checkedmember.status == discord.Status.do_not_disturb:
                status = "Do Not Disturb"
            else:
                status = "Offline"

            # Determine the user's activity
            activity = "None"
            if checkedmember.activity is not None:
                if isinstance(checkedmember.activity, discord.CustomActivity):
                    activity = checkedmember.activity.name
                elif isinstance(checkedmember.activity, discord.Spotify):
                    activity = f"Listening to {checkedmember.activity.title} by {checkedmember.activity.artist}"
                elif isinstance(checkedmember.activity, discord.Game):
                    activity = f"Playing {checkedmember.activity.name}"
                elif isinstance(checkedmember.activity, discord.Streaming):
                    activity = f"Streaming {checkedmember.activity.name}"

            # Get the user's join date
            joined_at = checkedmember.joined_at.strftime("%b %d, %Y %H:%M:%S")

            embed.title = f"{checkedmember.name}'s User Info"
            embed.set_thumbnail(url=checkedmember.display_avatar)
            embed.add_field(name="Nickname", value=checkedmember.nick or "None", inline=True)
            embed.add_field(name="Status", value=status, inline=True)
            embed.add_field(name="Activity", value=activity, inline=True)
            embed.add_field(name="Joined at", value=joined_at, inline=True)
            try:
                if isinstance(checkedmember.voice.channel.id, int):
                    voice_channel = checkedmember.voice.channel.mention
                    embed.add_field(name="Voice Channel", value=voice_channel, inline=False)
                else:
                    voice_channel = None
                    embed.add_field(name="Voice Channel", value="Not in a voice channel", inline=False)
            except:
                voice_channel = None
                embed.add_field(name="Voice Channel", value="Not in a voice channel", inline=False)


            try:
                member = interaction.guild.get_member(user.id)
                is_bot_owner = await self.bot.is_owner(interaction.user)
                if interaction.user.top_role >= member.top_role or member.id == interaction.user.id or is_bot_owner:

                    try:
                        query_cd = f"""
                        SELECT
                            SUM(CASE WHEN disconnectt > SUBDATE(CURRENT_TIMESTAMP, INTERVAL 24 HOUR) THEN playtime ELSE 0 END) as last_24_hours,
                            SUM(CASE WHEN disconnectt > SUBDATE(CURRENT_TIMESTAMP, INTERVAL 7 DAY) THEN playtime ELSE 0 END) as last_7_days,
                            SUM(CASE WHEN disconnectt > SUBDATE(CURRENT_TIMESTAMP, INTERVAL 30 DAY) THEN playtime ELSE 0 END) as last_30_days
                        FROM connectdisconnect
                        WHERE discord = {str(checkedmember.id)} AND serverapiid < 4
                        """

                        result_cd = await self.bot.get_cog('Database').execute_query_one(query_cd)
                        if result_cd:
                            embed.add_field(name="Today\'s Server Hours",
                                            value=await self.get_time_format(result_cd[0]), inline=False)
                            embed.add_field(name="Server Hours Last 7 Days",
                                            value=await self.get_time_format(result_cd[1]), inline=True)
                            embed.add_field(name="Server Hours Last 30 Days",
                                            value=await self.get_time_format(result_cd[2]), inline=True)
                    except Exception as e:
                        print(f"Error: {e}")

                    # Retrieve the most recent disconnect time
                    recent_disconnect = await self.get_recent_disconnect_time(checkedmember)
                    if recent_disconnect:
                        try:
                            dt = datetime.strptime(str(recent_disconnect[0]), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            tstamp = f'<t:{str(unix_timestamp)}:f>'
                            embed.add_field(name="Last Seen", value=tstamp, inline=False)
                        except Exception as e:
                            embed.add_field(name="Last Seen", value=str(recent_disconnect[0]), inline=False)

            except (discord.NotFound, discord.HTTPException, ValueError, AttributeError):
                pass

        # Send the embed to the channel
        embed.timestamp = interaction.created_at
        embed.set_footer(text='Created by discord.gg/ChromaLabs\u200b', icon_url=self.bot.user.avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @userinfocmds.command(name='revokebans', description='Revoke FalconEye AI Ban from API Logging DB')
    @app_commands.describe(member='Member who you wish to API Unban')
    async def user_revokebans(self, interaction: discord.Interaction, member: discord.User) -> None:
        await interaction.response.defer(thinking=True)
        requestingUser = interaction.user.id
        requestingUser = interaction.user.id

        admin = False
        mgmt = False

        if requestingUser in master_admins:
            admin = True

        role = Discord.utils.find(lambda r: r.id in mgmt_role_ids, interaction.user.roles)
        if role in interaction.user.roles:
            mgmt = True

        embed = generate_embed('Revoke User Ban')
        embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
        embed.add_field(name='Member', value=member.mention, inline=False)
        embed.add_field(name='Requester has access', value=(admin or mgmt), inline=False)
        embed.timestamp = interaction.created_at
        embed.set_footer(text='\u200b', icon_url=self.bot.user.avatar.url)
        await send_log_to_webhook(self.bot, embed)

        if (admin or mgmt):

            print(member)
            print(member.id)
            discordid=member.id

            # update information
            r = await self.bot.get_cog('Database').execute_query_one("UPDATE banlist SET revoked=1 WHERE discord=%s AND revoked = 0 AND banexp > CURRENT_TIMESTAMP", (str(discordid),), True)


            await interaction.followup.send(embed=interact_generate_embed(interaction, 'Requested Unban Queued for Processing'))

        else:
            await interaction.followup.send(embed=interact_generate_embed(interaction, 'You are not Worthy of revoking bans'))


    @userinfocmds.command(name='idents', description='Look up user identifiers')
    @app_commands.describe(member='Member whos identifiers you would like to lookup')
    async def user_idents(self, interaction: discord.Interaction, member: discord.User) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.followup.send(f"Please wait while the information you requested is gathered on {member.mention}", ephemeral=True)
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

        print(member)
        print(member.id)
        second_input=member.id


        embed = generate_embed('Lookup User Idents')
        embed.add_field(name='Requester', value=interaction.user.mention, inline=False)
        embed.add_field(name='Member', value=member.mention, inline=False)
        embed.add_field(name='Access Approved', value=(admin or mgmt or netg_unban or net_unban), inline=False)
        embed.timestamp = interaction.created_at
        embed.set_footer(text='\u200b', icon_url=self.bot.user.avatar.url)
        await send_log_to_webhook(self.bot, embed)

        # Check if user IDs are valid and the executing user's highest role is greater than each user's highest role


        try:
            member = interaction.guild.get_member(member.id)
            if interaction.user.top_role >= member.top_role or self.bot.owner_id == interaction.user.id:
                userIsSearchable = True
            else:
                userIsSearchable = False
        except Exception as e:
            userIsSearchable = True

        if admin:
            userIsSearchable = True

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
        fivem = ''
        time_stamp= ''
        embed_discord_ids = ''

        if (admin or mgmt or netg_unban or net_unban) and userIsSearchable:
            try:
                r = await self.bot.get_cog('Database').execute_query_one("SELECT pname, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, time_stamp, fivem FROM idents WHERE discord=%s ORDER BY time_stamp DESC LIMIT 1",(second_input,))
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
                    # Query to find all Discord IDs that match any of the fields

                    matching_discord_ids_query = '''
                    SELECT DISTINCT CONCAT('<@',discord,'>')
                    FROM idents
                    WHERE (steamid = %s AND steamid IS NOT NULL AND steamid != '')
                      OR (license = %s AND license IS NOT NULL AND license != '')
                      OR (xbl = %s AND xbl IS NOT NULL AND xbl != '')
                      OR (ip = %s AND ip IS NOT NULL AND ip != '')
                      OR (liveid = %s AND liveid IS NOT NULL AND liveid != '')
                      OR (hid0 = %s AND hid0 IS NOT NULL AND hid0 != '')
                      OR (hid1 = %s AND hid1 IS NOT NULL AND hid1 != '')
                      OR (hid2 = %s AND hid2 IS NOT NULL AND hid2 != '')
                      OR (hid3 = %s AND hid3 IS NOT NULL AND hid3 != '')
                      OR (hid4 = %s AND hid4 IS NOT NULL AND hid4 != '')
                      OR (hid5 = %s AND hid5 IS NOT NULL AND hid5 != '')
                      OR (hid6 = %s AND hid6 IS NOT NULL AND hid6 != '')
                      OR (hid7 = %s AND hid7 IS NOT NULL AND hid7 != '')
                      OR (hid8 = %s AND hid8 IS NOT NULL AND hid8 != '')
                      OR (hid9 = %s AND hid9 IS NOT NULL AND hid9 != '')
                      OR (fivem = %s AND fivem IS NOT NULL AND fivem != '')
                      AND discord IS NOT NULL AND discord != ''
                    '''
                    values = steamid, license, xbl, ip, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, fivem

                    # Execute the query
                    matching_discord_ids = await self.bot.get_cog('Database').execute_query(matching_discord_ids_query, values)

                    # Print the matching Discord IDs
                    if matching_discord_ids:
                        print("Matching Discord IDs:")
                        for discord_id in matching_discord_ids:
                            if discord_id[0] == '<@>':
                                pass
                            else:
                                embed_discord_ids = embed_discord_ids + f'\n {discord_id[0]}'
                embed = generate_embed('User Identifiers Requested')
                embed.color = 0xFDDA16
                embed.add_field(name='Player Name', value=pname, inline=False)
                embed.add_field(name='Discord', value=discord, inline=True)
                embed.add_field(name='Steam ID', value=steamid, inline=True)

                if admin:
                    embed.add_field(name='FiveM', value=fivem, inline=True)
                    embed.add_field(name='License', value=license, inline=False)
                    embed.add_field(name='XBL', value=xbl, inline=True)
                    embed.add_field(name='Live ID', value=liveid, inline=True)
                    embed.add_field(name='HID0', value=hid0, inline=False)
                    embed.add_field(name='HID1', value=hid1, inline=False)
                    embed.add_field(name='HID2', value=hid2, inline=False)
                    embed.add_field(name='HID3', value=hid3, inline=False)
                    embed.add_field(name='HID4', value=hid4, inline=False)
                    embed.add_field(name='HID5', value=hid5, inline=False)
                    embed.add_field(name='HID6', value=hid6, inline=False)
                    embed.add_field(name='HID7', value=hid7, inline=False)
                    embed.add_field(name='HID8', value=hid8, inline=False)
                    embed.add_field(name='HID9', value=hid9, inline=False)
                    ipLocation = await self.get_location_info(ip)
                    embed.add_field(name='IP', value=f'||{ip}||\n{ipLocation}', inline=True)
                elif mgmt:
                    embed.add_field(name='FiveM', value=fivem, inline=True)
                    embed.add_field(name='License', value=license, inline=False)
                    embed.add_field(name='XBL', value=xbl, inline=False)
                    embed.add_field(name='Live ID', value=liveid, inline=False)
                    embed.add_field(name='HID0', value=hid0, inline=False)
                    embed.add_field(name='HID1', value=hid1, inline=False)
                    embed.add_field(name='HID2', value=hid2, inline=False)
                    embed.add_field(name='HID3', value=hid3, inline=False)
                    embed.add_field(name='HID4', value=hid4, inline=False)
                    embed.add_field(name='HID5', value=hid5, inline=False)
                    embed.add_field(name='HID6', value=hid6, inline=False)
                    embed.add_field(name='HID7', value=hid7, inline=False)
                    embed.add_field(name='HID8', value=hid8, inline=False)
                    embed.add_field(name='HID9', value=hid9, inline=False)

                try:
                    dt = datetime.strptime(str(time_stamp), '%Y-%m-%d %H:%M:%S')
                    unix_timestamp = int(dt.timestamp())
                    tstamp = f'<t:{str(unix_timestamp)}:f>'
                    embed.add_field(name='Last Connection', value=tstamp, inline=True)
                except:
                    embed.add_field(name='Last Connection', value=time_stamp, inline=True)
                embed.add_field(name='Matching Discord IDs', value=embed_discord_ids, inline=False)
                embed.timestamp = datetime.utcnow()

                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.edit_message(embed=embed)
            except Exception as e:
                print(f"Error: {e}")
                messagedata = 'There was an error looking up: <@' + str(second_input) + '>'
                if interaction.response.is_done():
                    await interaction.followup.send(content=messagedata, ephemeral=True)
                else:
                    await interaction.response.edit_message(content=messagedata)
        else:
            messagedata = 'You are not Worthy of requesting User Information'
            if interaction.response.is_done():
                await interaction.followup.send(content=messagedata, ephemeral=True)
            else:
                await interaction.response.edit_message(content=messagedata)

    async def get_location_info(self, ip_address):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip_address}')
            data = response.json()
            returnstring = f"""
            ISP: `{data.get('isp')}`\n
            COUNTRY: `{data.get('country')}`\n
            CITY: `{data.get('city')}`\n
            REGION: `{data.get('regionName')}`\n
            ZIP: `{data.get('zip')}`\n
            """
            return returnstring
        except Exception as e:
            return {'error': str(e)}



async def setup(bot):
    await bot.add_cog(Commands(bot))
