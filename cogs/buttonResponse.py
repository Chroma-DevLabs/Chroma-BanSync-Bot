# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the 
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms 
# designated in the license will be met with swift judicial action by the author.
import asyncio

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally 
# bound to the terms stipulated in the license.
import discord
import discord as Discord
from discord import RawMemberRemoveEvent
from discord.ext import commands
from discord import app_commands
from discord.ui import View
from discord.utils import get
import datetime
from datetime import datetime, timedelta

from config import master_admins, net_unban_role_ids, netg_unban_role_ids, master_user_id, discord_ban_register_guild_id, mgmt_role_ids

# Dictionary to keep track of user cooldowns
user_verify_cooldowns = {}

class button_response(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_view_banlog(self, interaction, newlabel=None, remove=True, disable=True):
        message = interaction.message
        components = message.components
        view = View.from_message(message)  # Reconstruct the view from the message
        for item in view.children:
            if item.custom_id != interaction.data["custom_id"]:
                if remove:
                    view.remove_item(item)
            else:
                if newlabel:
                    item.label = newlabel
                else:
                    item.label += " Completed by: " + interaction.user.name
                if disable:
                    item.disabled = True
        # Update the message with the new view
        await interaction.followup.edit_message(message.id, view=view)


    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.message.author.id == self.bot.user.id:

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

            # Check which button was clicked using the custom_id
            if interaction.data["custom_id"].startswith('serverbanapproved'):
                await interaction.response.defer()
                _, id, banstaffdiscordid = interaction.data["custom_id"].split(':')


                if admin or mgmt or netg_unban:
                    await self.update_view_banlog(interaction, "Server Ban Approved by: " + interaction.user.name, remove=False, disable=True)
                    await interaction.followup.send("Server Ban Approved", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('serverbanrevoke'):
                #await interaction.response.defer()
                _, id, banstaffdiscordid = interaction.data["custom_id"].split(':')
                if admin or mgmt or netg_unban:
                    gself = self
                    interactiona = interaction
                    query = "SELECT discord from banlist WHERE id = %s"
                    parms = (int(id),)
                    baninfo = await self.bot.get_cog('Database').execute_query_one(query, parms)
                    if baninfo is not None:
                        if baninfo[0] is not None:
                            discordid = baninfo[0]
                            if interaction.user.id == int(discordid):
                                await interaction.response.defer()
                                await interaction.followup.send("You cannot revoke your own ban.")
                                # Timeout member for 28 days
                                try:
                                    timeout_time = discord.utils.utcnow() + timedelta(days=28)
                                    await interaction.user.timeout(timeout_time, reason=f'Attempting to revoke a server ban on themselves, {id}')
                                except:
                                    pass
                                return
                    # Open discord model for unban reason input
                    class UnbanReasonModel(discord.ui.Modal, title='UnServerBan'):
                        unbanreason = discord.ui.TextInput(label='Unban Reason', placeholder='Enter unban reason', min_length=5, max_length=2000)

                        async def on_submit(self, interaction: discord.Interaction):
                            #return self.unbanreason.value
                            print(self.unbanreason.value)
                            query = f"UPDATE banlist SET revoked = 1, revoke_discordid = {interactiona.user.id}, revoke_date = CURRENT_TIMESTAMP, revoke_reason = '{self.unbanreason.value}' WHERE (id={id} OR origin={id}) AND revoked = 0 AND banexp > CURRENT_TIMESTAMP"
                            logcur = await gself.bot.get_cog('Database').execute_query(query, None, True)

                            await interaction.response.send_message("Server Ban Revoked", ephemeral=True)
                            await gself.update_view_banlog(interactiona, "Server Ban Revoked by: " + interactiona.user.name, remove=True, disable=True)

                    view2 = UnbanReasonModel()
                    await interaction.response.send_modal(view2)
                    # trigger server unban command

                else:
                    await interaction.response.send_message("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('reminderdelete'):
                await interaction.response.defer()
                await interaction.message.delete()
                await interaction.followup.send("Message Deleted", ephemeral=True)

            elif interaction.data["custom_id"].startswith('serverbanremind'):
                await interaction.response.defer()

                if admin or mgmt or netg_unban or net_unban:
                    _, id, banstaffdiscordid = interaction.data["custom_id"].split(':')
                    query = """SELECT id, serverapiid, pname, pid, steamid, license, xbl, ip, discord, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, time_stamp, fivem, banreason, banexp, banstaffdiscordid
                    FROM banlist
                    WHERE id = %s
                    """
                    parms = (int(id),)
                    baninfo = await self.bot.get_cog('Database').execute_query_one(query, parms)
                    if baninfo:
                        id, serverapiid, pname, pid, steamid, license, xbl, ip, discordid, liveid, hid0, hid1, hid2, hid3, hid4, hid5, hid6, hid7, hid8, hid9, time_stamp, fivem, banreason, banexp, banstaffdiscordid = baninfo
                        ts = ''
                        try:
                            dt = datetime.strptime(str(time_stamp), '%Y-%m-%d %H:%M:%S')
                            unix_timestamp = int(dt.timestamp())
                            ts = f'{dt} UTC | <t:{str(unix_timestamp)}:f> | <t:{str(unix_timestamp)}:R>'
                        except Exception as e:
                            ts = ''
                        embed = discord.Embed(title=f"Ban Log Reminder", description='You are required to provide proper ban proof for all bans, regardless of the duration of the ban.',color=0xff0000)
                        embed.add_field(name='Player Name', value=pname, inline=True)
                        embed.add_field(name='Player ID', value=f'{pid}', inline=True)
                        embed.add_field(name='Reason', value=f"```{banreason}```", inline=False)
                        embed.add_field(name='Ban ID', value=f'NET-{str(id)}', inline=False)
                        embed.add_field(name='Time of Ban', value=ts, inline=False)
                        view = discord.ui.View()
                        # get the message link to the message the button pressed was in
                        url = interaction.message.jump_url
                        view.add_item(discord.ui.Button(label="Goto Ban Log", style=discord.ButtonStyle.green, url=url))
                        view.add_item(discord.ui.Button(label="Delete this message", style=discord.ButtonStyle.red, custom_id=f"reminderdelete:{id}"))
                        await self.bot.get_cog("messageSendQueue").send_message(type='user',
                                                                                userorchannelid=int(banstaffdiscordid),
                                                                                embed=embed,
                                                                                view=view
                                                                                )
                        await interaction.followup.send("Reminder Sent", ephemeral=True)
                    else:
                        await interaction.followup.send("Error looking up ban info to send ban log reminder!", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('discordkickapproved'):
                await interaction.response.defer()
                _, banneduserid, banstaffdiscordid = interaction.data["custom_id"].split(':')

                if admin or mgmt or netg_unban:
                    await self.update_view_banlog(interaction, "Discord Kick Approved by: " + interaction.user.name, remove=True, disable=True)
                    await interaction.followup.send("Discord Kick Approved", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('discordkickdenied'):
                await interaction.response.defer()
                _, banneduserid, banstaffdiscordid = interaction.data["custom_id"].split(':')
                if admin or mgmt or netg_unban:
                    await self.update_view_banlog(interaction, "Discord Kick Denied by: " + interaction.user.name, remove=True, disable=True)
                    await interaction.followup.send("Discord Kick Denied", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('discordkickremind') or interaction.data["custom_id"].startswith('discordbanremind'):
                await interaction.response.defer()
                if admin or mgmt or netg_unban:
                    _, kickeduserid, staffdiscordid = interaction.data["custom_id"].split(':')
                    embed = discord.Embed(title=f"Kick/Ban Log Reminder", description='You are required to provide proper proof for all Kicks & Bans.\n\nMultiple failurs to provide proof can result in removal of permissions, demotion or other punishments determinated by management/ownership.',color=0xff0000)
                    embed.add_field(name='User Name', value=f'<@{kickeduserid}>', inline=True)
                    embed.add_field(name='User Discord ID', value=f'```{kickeduserid}```', inline=True)
                    view = discord.ui.View()
                    # get the message link to the message the button pressed was in
                    url = interaction.message.jump_url
                    view.add_item(discord.ui.Button(label="Goto Kick/Ban Log", style=discord.ButtonStyle.green, url=url))
                    view.add_item(discord.ui.Button(label="Delete this message", style=discord.ButtonStyle.red, custom_id=f"reminderdelete:{staffdiscordid}"))
                    await self.bot.get_cog("messageSendQueue").send_message(type='user',
                                                                            userorchannelid=int(staffdiscordid),
                                                                            embed=embed,
                                                                            view=view
                                                                            )
                    await interaction.followup.send("Reminder Sent", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('discordbanapproved'):
                await interaction.response.defer()
                _, banneduserid, banstaffdiscordid = interaction.data["custom_id"].split(':')
                if admin or mgmt or netg_unban:
                    await self.update_view_banlog(interaction, "Discord Ban Approved by: " + interaction.user.name, remove=False, disable=True)
                    await interaction.followup.send("Discord Ban Approved", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('discordbanreviewneeded'):
                await interaction.response.defer()
                _, banneduserid, banstaffdiscordid = interaction.data["custom_id"].split(':')
                if admin or mgmt or netg_unban:
                    await self.update_view_banlog(interaction, "Discord Ban Review Needed Denied by: " + interaction.user.name, remove=False, disable=True)

                    await interaction.followup.send("Discord Ban Review Needed\n\nThis user needs to be unbanned.", ephemeral=True)
                else:
                    await interaction.followup.send("You are not worthy", ephemeral=True)

            elif interaction.data["custom_id"].startswith('discordbanrevoke'):
                _, banneduserid, banstaffdiscordid = interaction.data["custom_id"].split(':')
                if admin or mgmt or netg_unban:
                    # If error occurs for result nonetype then pass
                    user = await self.bot.fetch_user(int(banneduserid))
                    gbot = self.bot
                    gcogself = self
                    _interaction = interaction

                    # Open discord model for unban reason input
                    class UnbanReasonModel(discord.ui.Modal, title='Unglobalban'):
                        unbanreason = discord.ui.TextInput(label='Unban Reason', placeholder='Enter unban reason',
                                                           min_length=5, max_length=2000)

                        async def on_submit(self, interaction: discord.Interaction):
                            # return self.unbanreason.value
                            print(self.unbanreason.value)
                            reason = self.unbanreason.value
                            submitreason = ''

                            if reason:
                                submitreason = f"Unban Reason: {reason}"
                            else:
                                submitreason = "No Reason Provided"

                            guild = gbot.get_guild(discord_ban_register_guild_id)
                            if guild:
                                member = guild.get_member(int(banneduserid))
                                if member:
                                    await member.unban(reason=submitreason)
                                    await _interaction.response.send_message("Discord Ban Revoked", ephemeral=True)
                                    await gcogself.update_view_banlog(_interaction, "Discord Ban Revoked by: " + _interaction.user.name, remove=True, disable=True)
                                else:
                                    await _interaction.followup.send("Error unbanning user", ephemeral=True)
                            else:
                                await _interaction.followup.send("Error unbanning user", ephemeral=True)
                    view2 = UnbanReasonModel()
                    await interaction.response.send_modal(view2)
                else:
                    await interaction.response.send_message("You are not worthy", ephemeral=True)


async def setup(bot):
    await bot.add_cog(button_response(bot))
