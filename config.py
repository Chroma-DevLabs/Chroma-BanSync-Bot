# General Config
import os
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.

token = os.getenv('token')
webhook = os.getenv('main_webhook_url')
master_user_id = int(os.getenv('master_user_id'))
database_config = {
    "user": os.getenv('dbuser'),
    "host": os.getenv('dbhost'),
    "port": int(os.getenv('dbport')),
    "password": os.getenv('dbpass'),
    "database": os.getenv('dbname'),
}

discord_ban_register_guild_id = int(os.getenv('discord_ban_register_guild_id'))
discord_ban_log_channel_id = int(os.getenv('discord_ban_log_channel_id'))
game_ban_log_channel_id = int(os.getenv('game_ban_log_channel_id'))


# Int Arrays
master_admins = [int(x) for x in os.getenv('master_admins').split(',')]

net_unban_role_ids = [int(x) for x in os.getenv('net_unban_role_ids').split(',')]
netg_unban_role_ids = [int(x) for x in os.getenv('netg_unban_role_ids').split(',')]
mgmt_role_ids = [int(x) for x in os.getenv('mgmt_role_ids').split(',')]
server_api_ids = [int(x) for x in os.getenv('server_api_ids').split(',')]