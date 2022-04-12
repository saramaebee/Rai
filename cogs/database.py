import concurrent.futures
import functools
import time

import discord
from discord.ext import commands, tasks
from .utils import helper_functions as hf
import sqlite3
import os
import asyncio

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


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

    def queue_setup(self):
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
        except Exception as e:
            result = e
            print(f"error here: {e}", type(e))
            # raise e
        # print("commit", self.db.commit())
        # print("close", c.close())
        print('result', result)
        return result

    # Currently not using, this is old code
    async def _access_db(self, query):
        return self.db.execute(query).fetchall()  # potential for SQL injection?

    # Currently not using, this is old code
    async def access_db(self, query):  # run access to db as a
        return
        try:
            result = await self.loop.run_in_executor(None, functools.partial(self.db.execute, query))
            return result.fetchall()
        except Exception as e:
            raise
        # return self.loop.run_until_complete(self._access_db(query))

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        try:
            result = await self.access_db(query)
            if result:
                await hf.safe_send(ctx, result)
            else:
                await hf.safe_send(ctx, "None")
        except Exception as e:
            print(e, e.args, type(e))
            raise

        # old way used below line
        # await self.add_to_queue(query)

    def callback(self, future):
        if future.exception():
            print("callback future exception", future.exception(), type(future.exception()))

    async def add_to_queue(self, query):
        if not self.queue:
            # with concurrent.futures.ThreadPoolExecutor() as pool:
            try:
                blocking = await self.loop.run_in_executor(None, self.queue_setup)
            except Exception as e:
                print("blocking exception", e, type(e))
                raise

            try:
                results = await asyncio.gather(blocking, return_exceptions=True)
                print("finished", results[0], type(results[0]))
            except Exception as e:
                print("exception!", e, type(e))
                raise

            # result = [t.result() for t in completed][0]
            # exception = [t.exception() for t in completed][0]
            # print("after blocking", result, type(result))
            # print("exceptions from future: ", exception, type(exception))
        await self.queue.put(query)

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
                try:
                    # result = self.execute(query)
                    result = self.raise_exception()
                    print("worker result", result, type(result))
                except Exception as e:
                    print("worker error, ", e, type(e))
                    # raise

                # Notify queue that task is done
                queue.task_done()


def setup(bot):
    bot.add_cog(Database(bot))
