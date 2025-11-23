import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from utils import database, variables, colors, views, images, valorant_handler
import tempfile
import os
import valaw
import aiohttp

users_db = database.Users()
website_db = database.Website()
valorantInfo_db = database.ValorantInfo()
riot_db = database.RiotAPICollection()
valawClient = valaw.Client(variables.RIOT_API_KEY, cluster="americas")

class DeveloperCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="dm_user", description="Send a message to a user", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def dm_user(self, interaction: nextcord.Interaction, message: str, users_ids: str = SlashOption(name="users_id", description="A user's ID or multiple user IDs separated by a space")):
        # Split user IDs and process the message
        user_ids = users_ids.split(" ")
        def process_string(input_string):
            return bytes(input_string, "utf-8").decode("unicode_escape")

        processed_message = process_string(message)
        
        # Fetch user objects and mentions
        users = [self.bot.get_user(int(user_id)) for user_id in user_ids]
        mentions = " ".join(user.mention for user in users if user is not None)
        
        embed = nextcord.Embed(description=processed_message, color=colors.primary)
        embed.set_author(name="VALcord Development Team", icon_url=self.bot.user.avatar.url)
        
        view = views.SendMessageView(interaction, users, embed)
        await interaction.response.send_message(f"Do you want to send this to: {mentions}:", embed=embed, view=view, ephemeral=True)

    @nextcord.slash_command(name="page_views", description="Get the page views of the website", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def page_views(self, interaction: nextcord.Interaction):
        page_views = website_db.get_many_page_views()
    
        # Create a temporary file to store the page views data
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            # Write the page views data to the temporary file
            for page_view in page_views:
                temp_file.write(f"{page_view['url']}: {page_view['views']}\n")
        
        # Send the temporary file as a message attachment
        with open(temp_file.name, "rb") as file:
            await interaction.response.send_message(file=nextcord.File(file, "page_views.txt"), ephemeral=True)

        # Delete the temporary file
        os.remove(temp_file.name)

    @nextcord.slash_command(name="server_count", description="Get the server count of the bot", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def server_count(self, interaction: nextcord.Interaction):
        server_count = len(self.bot.guilds)
        await interaction.response.send_message(f"The bot is in {server_count} servers.", ephemeral=True)

    @nextcord.slash_command(name="user_count", description="Get the user count of the bot", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def user_count(self, interaction: nextcord.Interaction):
        user_count = len(self.bot.users)
        await interaction.response.send_message(f"The bot has {user_count} users.", ephemeral=True)

    @nextcord.slash_command(name="send_message", description="Send a message to a channel", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def send_message(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel, message: str, embed_message: bool):
        if embed_message:
            embed = nextcord.Embed(description=message, color=colors.primary)
            message = None
        else:
            embed = None
        await channel.send(message, embed=embed)
        await interaction.response.send_message("Message Sent")
    
    @nextcord.slash_command(name="update_topgg", description="Update the top.gg stats of the bot", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def update_topgg(self, interaction: nextcord.Interaction):
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://top.gg/api/bots/{self.bot.user.id}/stats", data={"server_count": len(self.bot.guilds)}, headers={"Authorization": variables.TOPGG_TOKEN})
        await interaction.response.send_message("Updated top.gg stats.", ephemeral=True)

    @nextcord.slash_command(name="test", description="Test command", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
    async def test(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("This is a test\ncommand.")


def setup(bot):
    bot.add_cog(DeveloperCog(bot))