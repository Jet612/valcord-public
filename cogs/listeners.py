import nextcord
from nextcord.ext import commands
import traceback
import aiohttp
import os
from utils import variables, database, colors

guilds_db = database.Guilds()

class ListenCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")
        if not os.getenv("BETA_MODE"):
            async with aiohttp.ClientSession() as session:
                await session.post(f"{os.getenv('IPC_CLIENT_URL', 'http://localhost:5000')}/restart", headers={"Authorization": variables.IPC_SECRET})
                print("Reconnected IPC Client.")
        else:
            await self.bot.change_presence(
                activity=nextcord.Activity(type=nextcord.ActivityType.competing, name="BETA OLYMPICS"))

        channel = self.bot.get_channel(int(os.getenv("STARTUP_CHANNEL_ID", "0")))
        embed = nextcord.Embed(title="Startup", description="Bot has restarted.", color=nextcord.Color.green())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await channel.send(embed=embed, content=f"<@!{os.getenv('BOT_OWNER_ID', '0')}>")

    @commands.Cog.listener()
    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc server is ready.")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: nextcord.Guild):
        guilds_db.create_guild(guild.id)
        embed = nextcord.Embed(title="Guild Joined", color=colors.primary)
        if guild.icon:
            icon = guild.icon.url
        else:
            icon = None
        embed.set_author(name=guild.name, icon_url=icon)
        embed.add_field(name="ID", value=f"```{guild.id}```", inline=True)
        embed.add_field(name="Owner", value=f"```{guild.owner.name} ({guild.owner.id})```", inline=True)
        embed.add_field(name="Members", value=f"```{guild.member_count}```", inline=True)
        embed.add_field(name="Created", value=f"<t:{guild.created_at}:R>")
        await self.bot.get_guild(variables.VALCORD_GUILD_ID).get_channel(variables.DEVLELOPER_LOGS_CHANNEL_ID).send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: nextcord.Guild):
        guilds_db.delete_guild({"guild_id": guild.id})
        embed = nextcord.Embed(title="Guild Left", color=colors.primary)
        if guild.icon:
            icon = guild.icon.url
        else:
            icon = None
        embed.set_author(name=guild.name, icon_url=icon)
        embed.add_field(name="ID", value=f"```{guild.id}```", inline=True)
        embed.add_field(name="Owner", value=f"```{guild.owner.name} ({guild.owner.id})```", inline=True)
        embed.add_field(name="Members", value=f"```{guild.member_count}```", inline=True)
        embed.add_field(name="Created", value=f"<t:{guild.created_at}:R>")
        await self.bot.get_guild(variables.VALCORD_GUILD_ID).get_channel(variables.DEVLELOPER_LOGS_CHANNEL_ID).send(embed=embed)
            

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, exception):
        try:
            exception = getattr(exception, "original", exception)
            if isinstance(exception, commands.CommandOnCooldown):
                await interaction.response.send_message(f"This command is on cooldown. Please try again in {exception.retry_after:.2f}s.", ephemeral=True)
            else:
                error_channel = self.bot.get_channel(int(os.getenv("ERROR_CHANNEL_ID", "0")))
                dev_embed = nextcord.Embed(title=f"User: {interaction.user.id} ({interaction.user.name})", color=nextcord.Color.red())
                dev_embed.add_field(name="Guild", value=f"{interaction.guild.id} ({interaction.guild.name})", inline=False)
                dev_embed.add_field(name="Channel", value=f"{interaction.channel.id} ({interaction.channel.name})", inline=False)
                dev_embed.add_field(name="Interaction ID", value=f"{interaction.id}", inline=False)
                dev_embed.add_field(name="Basic Exception", value=f"{str(exception)}", inline=False)
                traceback_message = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
                dev_embed.add_field(name="Traceback", value=f"```{traceback_message}```", inline=False)
                await error_channel.send(embed=dev_embed)

                embed = nextcord.Embed(title="An Error Occurred", description=f"{str(exception)}", color=nextcord.Color.red())
                embed.set_footer(text="A report has been sent to the developers.")
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            traceback.print_exc()

def setup(bot):
    bot.add_cog(ListenCog(bot))