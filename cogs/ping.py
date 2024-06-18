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



class ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name='ping', description='Ping command to check the bot\'s latency.')
    async def ping(self, interaction: discord.Interaction) -> None:
        """Ping command to check the bot's latency."""
        await interaction.response.defer(thinking=True, ephemeral=True)
        latency = round(self.bot.latency * 1000)
        if latency > 100:
            color = 0xFF0000
        elif latency > 50:
            color = 0xFFA500
        else:
            color = 0x00FF00
        embed = discord.Embed(title="Pong!", description=f"Latency: {latency}ms", color=color)
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ping(bot))
