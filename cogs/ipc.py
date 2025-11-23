import nextcord
from nextcord.ext import commands, ipc
from utils import database, variables, views
import valaw
import os
from datetime import datetime

guilds_db = database.Guilds()
users_db = database.Users()
website_db = database.Website()
votes_db = database.Votes()
valorantClient = valaw.Client(token=variables.RIOT_API_KEY, cluster="americas")

class IpcCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @ipc.server.route()
    async def rso_callback(self, data):
        users_db.update_user({"uuid": data.uuid}, {"access_token": data.tokenData["access_token"], "refresh_token": data.tokenData["refresh_token"], "api_puuid": data.responseData["puuid"]})
        return True
    
    @ipc.server.route()
    async def invite(self, data):
        return True

    @ipc.server.route()
    async def page_viewed(self, data):
        website_db.add_page_view(data.url)

    @ipc.server.route()
    async def topgg_vote(self, data):
        timestamp = int(datetime.now().timestamp())
        channel = self.bot.get_channel(int(os.getenv("VOTES_CHANNEL_ID", "0")))
        reminders = votes_db.get_user({"user_id": int(data.data.get("user"))})
        if reminders is None:
            votes_db.add_user(int(data.data.get("user")), timestamp)
            reminders = votes_db.get_user({"user_id": int(data.data.get("user"))})
        else:
            votes_db.update_user({"user_id": int(data.data.get("user"))}, {"timestamp": timestamp})
        embed = nextcord.Embed(title="Thanks for voting for VALcord!", description=f"Don't forget to vote again <t:{timestamp+43200}:R>!")
        message = await channel.send(content=f"<@!{int(data.data.get('user'))}>", embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(IpcCog(bot))