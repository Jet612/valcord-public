import nextcord
from nextcord.ext import commands, tasks
import os
from utils import database, variables, views
from datetime import datetime

votes_collection = database.Votes()

class VotesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vote_reminder.start()

    @tasks.loop(minutes=1)
    async def vote_reminder(self):
        now = int(datetime.now().timestamp())
        voters = votes_collection.get_many_users()
        for voter in voters:
            if voter["remind"] and voter["timestamp"] + 43200 <= now and voter["timestamp"] != 0:
                user = self.bot.get_user(voter["user_id"])
                if user:
                    await user.send(f"Hey! You can vote again! https://top.gg/bot/{os.getenv('BOT_ID', '0')}/vote")
                    votes_collection.update_user({"user_id": voter["user_id"]}, {"timestamp": 0})


def setup(bot: commands.Bot):
    bot.add_cog(VotesCog(bot))