import discord
from discord.ext import commands
from .utils import helper_functions as hf
import sqlite3
import os
import asyncio

dir_path = os.path.dirname(os.path.realpath(__file__))
_loop = asyncio.get_event_loop()


class Database(commands.Cog):
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(f"{dir_path}/database.db"):
            db = open(f"{dir_path}/database.db", "w")
            db.close()

    class Db(object):
        def __enter__(self):
            self.conn = sqlite3.connect(f"{dir_path}/database.db")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.conn.close()

        def execute(self, query):
            c = self.conn.cursor()
            try:
                result = c.execute(query)
                self.conn.commit()
            except Exception as e:
                result = e
            return result

    def _access_db(self, query):
        with self.Db() as db:  # idk if it's good to completely open and close DB at each access
            return db.execute(query).fetchall()  # potential for SQL injection?

    async def access_db(self):  # run access to db as a
        await _loop.run_in_executor(None, self._access_db)


def setup(bot):
    bot.add_cog(Database(bot))
