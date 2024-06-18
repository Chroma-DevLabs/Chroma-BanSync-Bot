# The aforementioned code and documents are protected and released to the public under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License which can be viewed in license.md or on the 
# Creative Commons website (https://creativecommons.org/licenses/by-nc/4.0/). Any failure to comply with the terms 
# designated in the license will be met with swift judicial action by the author. 

# By downloading, executing or otherwise transferring the contents of this repository by any means you are legally 
# bound to the terms stipulated in the license.
import discord


def generate_embed(title: str, description: str = None) -> discord.Embed:
    """Generates a generic embed

    Args:
        ctx (commands.context): Context of the invoked command
        title (str): The title of the embed
        description (str, optional): The description for the embed. Defaults to None.

    Returns:
        discord.Embed: Formatted discord embed object
    """

    embed = discord.Embed(description=description, colour=0xc706ce)
    embed.set_author(name=title)

    return embed
