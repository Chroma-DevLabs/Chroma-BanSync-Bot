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

class help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='about', description='About this bot')
    async def about(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        requestingUser = interaction.user.id

        embed = discord.Embed(title="About", description="This bot is designed by [ChromaLabs](https://discord.gg/ChromaLabs) for Ban Management.", color=0xCB35FF)
        embed.add_field(name="FiveM Script", value="https://chromalabs.tebex.io/package/6315042", inline=False)
        embed.add_field(name="Uptime", value=f'<t:{str(self.bot.startupTimestampInt)}:R>', inline=False)
        embed.set_footer(text="discord.gg/ChromaLabs")

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(help(bot))
