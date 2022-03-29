import concurrent.futures

import discord
from discord.ext import commands, tasks
from .utils import helper_functions as hf
import sqlite3
import os
import asyncio

dir_path = os.path.dirname(os.path.realpath(__file__))


def open_database():
    return sqlite3.connect(f"{dir_path}/database.db", check_same_thread=False)


class Database(commands.Cog):
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot
        self.db = open_database()
        self.queue = self.task = None
        self.loop = asyncio.get_event_loop()
        if not self.save_sqlite_db.is_running():
            self.save_sqlite_db.start()

    async def queue_setup(self):
        print("queue before", self.queue)
        self.queue = asyncio.Queue()
        print("queue after", self.queue)
        self.task = self.loop.create_task(self.worker("Busy boy", self.queue))
        print("queue final")

    def cog_unload(self):
        self.task.cancel()
        # src: https://docs.python.org/3/library/asyncio-queue.html

    @tasks.loop(minutes=5.0)
    async def save_sqlite_db(self):
        self.db.commit()

    def execute(self, query):
        c = self.db.cursor()
        try:
            result = c.execute(query)
            self.db.commit()
        except Exception as e:
            result = e
        return result

    # Currently not using, this is old code
    async def _access_db(self, query):
        return self.db.execute(query).fetchall()  # potential for SQL injection?

    # Currently not using, this is old code
    async def access_db(self, query):  # run access to db as a
        return self.loop.run_until_complete(self._access_db(query))

    async def add_to_queue(self, query):
        if not self.queue:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                blocking = [await self.loop.run_in_executor(pool, self.queue_setup)]
                completed, pending = await asyncio.wait(blocking)
                result = [t.result() for t in completed][0]
                print("after blocking", result)
        await self.queue.put(query)

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        await self.add_to_queue(query)

    async def worker(self, name, queue):
        while True:
            # Get a sql command out of the queue
            try:
                query = queue.get_nowait()
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
