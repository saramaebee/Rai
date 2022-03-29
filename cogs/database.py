import discord
from discord.ext import commands, tasks
from .utils import helper_functions as hf
import sqlite3
import os
import asyncio

dir_path = os.path.dirname(os.path.realpath(__file__))
_loop = asyncio.get_event_loop()


def open_database():
    return sqlite3.connect(f"{dir_path}/database.db", check_same_thread=False)


class Database(commands.Cog):
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        self.db = open_database()
        self.queue = self.task = None
        asyncio.run(self.queue_setup())
        if not self.save_sqlite_db.is_running():
            self.save_sqlite_db.start()

    async def queue_setup(self):
        self.queue = asyncio.Queue()
        self.task = await asyncio.create_task(self.worker("Busy boy", self.queue))

    async def cog_unload(self):
        self.task.cancel()
        await asyncio.gather(self.task, return_exceptions=True)
        # src: https://docs.python.org/3/library/asyncio-queue.html

    @tasks.loop(minutes=5.0)
    async def save_sqlite_db(self):
        self.db.commit()

    def execute(self, query):
        c = self.db.cursor()
        try:
            result = c.execute(query)
            self.db.commit()
            print(0)
        except Exception as e:
            result = e
        return result

    async def _access_db(self, query):
        return self.db.execute(query).fetchall()  # potential for SQL injection?

    async def access_db(self, query):  # run access to db as a
        return _loop.run_until_complete(self._access_db(query))

    def add_to_queue(self, query):
        self.queue.put(query)

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        self.add_to_queue(query)

    async def worker(self, name, queue):
        while True:
            # Get a sql command out of the queue
            try:
                query = await queue.get_nowait()
            except asyncio.QueueEmpty:
                # Wait a bit if queue is empty
                await asyncio.sleep(1)
            else:
                # Perform task
                result = self.execute(query)
                print(result)

                # Notify queue that task is done
                queue.task_done()


def setup(bot):
    bot.add_cog(Database(bot))
