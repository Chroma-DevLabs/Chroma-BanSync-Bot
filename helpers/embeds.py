import discord
from discord.ext import commands


def interact_generate_embed(interaction: discord.Interaction, title: str, description: str = None):
    if description:

        # Create embed object

        embed = discord.Embed(description=description,
                              colour=0xFFFFFF)

    else:

        # Create embed object

        embed = discord.Embed(colour=0xFFFFFF)

    # Use author as title as it looks better

    embed.set_author(name=title)

    # Create footer that shows who requested the command

    if hasattr(interaction.user, 'avatar.url'):
        avatar_url = interaction.user.avatar.url
    else:
        avatar_url = None
    embed.set_footer(text='Command requested by ' + interaction.user.display_name, icon_url=avatar_url)


    # Return the embed

    return embed

def interact_generate_embed_assign(interaction: discord.Interaction, type: str, title: str, description: str = None):
    if description:

        # Create embed object
        if type == 'assign':
            embed = discord.Embed(description=description,
                                  colour=0x33FF33)
        elif type == 'unassign':
            embed = discord.Embed(description=description,
                                  colour=0xFF3333)
        else:
            embed = discord.Embed(description=description,
                                  colour=0xFFFFFF)

    else:

        # Create embed object

        if type == 'assign':
            embed = discord.Embed(colour=0x33FF33)
        elif type == 'unassign':
            embed = discord.Embed(colour=0xFF3333)
        else:
            embed = discord.Embed(colour=0xFFFFFF)

    # Use author as title as it looks better

    embed.set_author(name=title)

    # Create footer that shows who requested the command

    if hasattr(interaction.user, 'avatar.url'):
        avatar_url = interaction.user.avatar.url
    else:
        avatar_url = None
    embed.set_footer(text='Command requested by ' + interaction.user.display_name, icon_url=avatar_url)


    # Return the embed

    return embed

def interact_generate_embed_color(interaction: discord.Interaction, type: str, title: str, description: str = None, colour: int = 0xFFFFFF):
    if description:
        embed = discord.Embed(description=description,
                              colour=colour)

    else:
        embed = discord.Embed(colour=colour)

    # Use author as title as it looks better

    embed.set_author(name=title)

    # Create footer that shows who requested the command

    if hasattr(interaction.user, 'avatar.url'):
        avatar_url = interaction.user.avatar.url
    else:
        avatar_url = None
    embed.set_footer(text='Command requested by ' + interaction.user.display_name, icon_url=avatar_url)


    # Return the embed

    return embed


def error(ctx: commands.Context, text: str) -> discord.Embed:
    """Generates a standardized error embed

    Args:
        ctx (discord.Context): Message context
        text (str): The text the embed should contain

    Returns:
        discord.Embed: The formatted error embed
        
    """

    # Create Error Embed

    embed = discord.Embed(description=text,
                          colour=0xFF0000)

    embed.set_author(name='Caught exception.')

    if hasattr(ctx.author, 'avatar_url'):
        avatar_url = ctx.author.avatar_url
    else:
        avatar_url = None
    embed.set_footer(text='Command requested by ' +
                          ctx.author.display_name, icon_url=avatar_url)

    return embed
