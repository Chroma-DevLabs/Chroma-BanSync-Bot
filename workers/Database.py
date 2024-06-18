import discord
from discord.ext import commands
import aiomysql
import asyncio
from config import database_config

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_pool())
        
    async def create_pool(self, retries=10, delay=30):  # adding a retry and delay parameter
        for _ in range(retries):
            try:
                if hasattr(self, 'pool'):
                    self.pool.close()
                    await self.pool.wait_closed()
                self.pool = await aiomysql.create_pool(user=database_config['user'],
                                                       password=database_config['password'],
                                                       host=database_config['host'],
                                                       port=int(database_config['port']),
                                                       db=database_config['database'],
                                                       loop=self.bot.loop)
                return  # If connection is successful, exit the function
            except aiomysql.OperationalError as e:
                if "Can't connect to MySQL server" in str(
                        e) and _ < retries - 1:  # Check if it's a connection error and not the last retry
                    print(f"Failed to connect to MySQL server. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)  # Wait for some time before retrying
                else:
                    print(
                        f"Failed to connect to MySQL server after {retries} attempts. Please check your connection settings.")
                    raise e  # Raise the exception if it's the last retry or if it's another type of error


    async def execute_query(self, query, values=None, insert=True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if values:
                        await cur.execute(query, values)
                    else:
                        await cur.execute(query)
                    if insert:
                        await conn.commit()
                    return await cur.fetchall()
                except Exception as e:
                    print(f"Database error: {str(e)}")
                    if "Lost connection to MySQL server during query" in str(e):
                        await self.create_pool()

    async def execute_query_one(self, query, values=None, insert=True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if values:
                        await cur.execute(query, values)
                    else:
                        await cur.execute(query)
                    if insert:
                        await conn.commit()
                    return await cur.fetchone()
                except Exception as e:
                    print(f"Database error: {str(e)}")
                    if "Lost connection to MySQL server during query" in str(e):
                        await self.create_pool()

    async def execute_query_many(self, query, values=None, insert=True):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if values:
                        await cur.executemany(query, values)
                    else:
                        await cur.executemany(query)
                    if insert:
                        await conn.commit()
                    return await cur.fetchall()
                except Exception as e:
                    print(f"Database error: {str(e)}")
                    if "Lost connection to MySQL server during query" in str(e):
                        await self.create_pool()

    async def close(self):
        self.pool.close()
        await self.pool.wait_closed()

    async def cog_unload(self):
        await self.close()

async def setup(bot):
    await bot.add_cog(Database(bot))