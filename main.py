import config
import discord
from discord.ext import commands
import os
import logging
from config import token
import asyncio

import os
import datetime

import pytz

# Define intents
#from helpers.members import update_or_add_member

intents = discord.Intents(messages=True, guilds=True, members=True, reactions=True, voice_states=True, bans=True, message_content=True, presences=True)

# Initialize bot and remove default command
bot = commands.Bot('bansync!', description="Ban Sync", intents=intents)
bot.remove_command('help')

# Create Custom Logger

logger = logging.getLogger(__name__)

# Create a handler that points to bot.log

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename=os.getcwd() + 'bot.log', encoding='utf-8', mode='w')

# Set logging levels

stream_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.WARN)

# Format handler outputs

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s -- %(message)s', datefmt='%d-%b-%y %H:%M:%S')

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Assign handlers to logger

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

bot.logger = logger


@bot.event
async def on_ready():

    bot.startupComplete = False

    loaded_cogs = 0
    loaded_workers = 0

    # Load all cogs in the cogs folder
    # Iterate through filenames using iterable cog

    for cog in os.listdir('workers/'):

        # Check if filename is a valid python file

        if cog.endswith('.py'):
            # Use a slice to remove the file extension
            # to get the cog name

            cog_name = cog[:-3]

            # Have the bot load the cog

            await bot.load_extension('workers.' + cog_name)

            # Add one to the loaded cogs value

            loaded_workers += 1

    # Use os.walk() to traverse through all subdirectories and files in cogs/
    for root, dirs, files in os.walk('cogs/'):
        for file in files:
            # Check if the file is a valid python file (ends with .py)
            if file.endswith('.py'):
                # Get the full path to the python file
                cog_path = os.path.join(root, file)

                # Get the relative path of the python file inside cogs/ directory
                # This will be used as the cog name
                cog_name = os.path.relpath(cog_path, 'cogs')[:-3].replace(os.path.sep, '.')

                # Have the bot load the cog
                await bot.load_extension('cogs.' + cog_name)

                # Add one to the loaded cogs value
                loaded_cogs += 1


    await bot.tree.sync()

    # Debug message on startup

    print('-' * 32)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(f'Loaded {loaded_cogs} cogs')
    print(f'Loaded {loaded_workers} workers')

    
    print('-' * 12 + ' Guilds ' + '-' * 12)
    guildCount = 0
    async for guild in bot.fetch_guilds(limit=150):
        await bot.tree.sync(guild=guild)
        guildCount += 1
        await asyncio.sleep(1)
        print(guild.name)
    print('-' * 32)

    await asyncio.sleep(1)
    embed = discord.Embed(title='Bot Started', description=f'Bot has started successfully')
    embed.colour = discord.Colour.green()
    embed.add_field(name='Bot', value=f'{bot.user.name}\n{bot.user.id}')
    embed.add_field(name='Guild Count', value=f'{guildCount}')
    embed.add_field(name='Loaded Workers', value=f'{loaded_workers}')
    embed.add_field(name='Loaded Cogs', value=f'{loaded_cogs}')
    embed.timestamp = discord.utils.utcnow()
    embed.set_footer('Created by discord.gg/ChromaLabs')
    await bot.get_cog("WebhookLogger").send_log_to_webhook(embed)
    try:
        master_user = bot.get_user(config.master_user_id)
        await master_user.send(embed=embed, delete_after=10)
    except Exception as e:
        print(f'Error sending message to owner: {e}')

    bot.startupTimestampInt = int(datetime.datetime.utcnow().timestamp())

    bot.startupComplete = True


bot.run(token)
