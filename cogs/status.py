import nextcord
from nextcord.ext import commands, tasks
import psutil
import os
from utils import database, colors

users_db = database.Users()

class Status:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cpu_usage = psutil.cpu_percent()
        self.servers = len(self.bot.guilds)
        self.tracked_users = len(users_db.get_many_users())

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.status = Status(bot)
        self.status_option = 1
        self.update_cpu_usage.start()
        self.update_servers_and_tracked_users.start()
        self.update_activity.start()

    @tasks.loop(seconds=30)
    async def update_activity(self):
        await self.bot.wait_until_ready()
        if self.status_option == 1:
            self.status_option = 2
            await self.bot.change_presence(
                activity=nextcord.Activity(type=nextcord.ActivityType.playing, name="VALORANT"))
        elif self.status_option == 2:
            self.status_option = 3
            await self.bot.change_presence(
                activity=nextcord.Activity(type=nextcord.ActivityType.playing, name="V2 INCOMING!"))
        elif self.status_option == 3:
            self.status_option = 4
            await self.bot.change_presence(
                activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="Game Replays"))
        elif self.status_option == 4:
            self.status_option = 1
            await self.bot.change_presence(
                activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="Ranked Matches"))

    @tasks.loop(seconds=30)
    async def update_cpu_usage(self):
        await self.bot.wait_until_ready()
        self.status.cpu_usage = psutil.cpu_percent()
        await self.update_embed()

    @tasks.loop(hours=1)
    async def update_servers_and_tracked_users(self):
        await self.bot.wait_until_ready()
        self.status.servers = len(self.bot.guilds)
        self.status.tracked_users = len(users_db.get_many_users())
        await self.update_embed()

    async def update_embed(self):
        embed = nextcord.Embed(color=colors.primary)
        embed.set_author(name="VALcord Status", icon_url=self.bot.user.avatar.url)
        embed.add_field(name="Servers", value=f"```{self.status.servers}```", inline=True)
        embed.add_field(name="Tracked Users", value=f"```{self.status.tracked_users}```", inline=True)
        embed.add_field(name="CPU Usage", value=f"```{self.status.cpu_usage}%```", inline=True)
        message = await self.bot.get_channel(int(os.getenv("STATUS_CHANNEL_ID", "0"))).fetch_message(int(os.getenv("STATUS_MESSAGE_ID", "0")))
        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(StatusCog(bot))