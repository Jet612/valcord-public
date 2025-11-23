import nextcord
from nextcord.ext import commands, tasks
from utils import database, colors, views

guilds_db = database.Guilds()

class ServerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_guilds.start()

    @nextcord.slash_command(name="server-settings", description="View the server's settings", default_member_permissions=nextcord.Permissions(administrator=True))
    async def server_settings(self, interaction: nextcord.Interaction):
        server_data = guilds_db.get_guild({"guild_id": interaction.guild.id})
        if not server_data:
            guilds_db.create_guild(interaction.guild.id)
            server_data = guilds_db.get_guild({"guild_id": interaction.guild.id})
        embed = nextcord.Embed(title="Server Settings", color=colors.primary)
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
        embed.add_field(name="Log Channel", value=server_data["log_channel"], inline=False)
        embed.add_field(name="News", value=f"**Enabled:** {server_data['news']}\n**Channel:** {server_data['news_channel']}", inline=False)
        embed.add_field(name="Patch Notes", value=f"**Enabled:** {server_data['patch_notes']}\n**Channel:** {server_data['patch_notes_channel']}", inline=False)
        embed.add_field(name="Linked Roles", value=f"_Coming Soon_", inline=False)

        view = views.ServerSettingsView(interaction, server_data)
        return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @tasks.loop(hours=3)
    async def check_guilds(self):
        await self.bot.wait_until_ready()
        guild_ids_in_db = set(guild["guild_id"] for guild in guilds_db.get_many_guilds())
        bot_guild_ids = set(guild.id for guild in self.bot.guilds)
        for guild_id in guild_ids_in_db - bot_guild_ids:
            guilds_db.delete_guild({"guild_id": guild_id})
        for guild_id in bot_guild_ids - guild_ids_in_db:
            guilds_db.create_guild(guild_id)


def setup(bot):
    bot.add_cog(ServerCog(bot))