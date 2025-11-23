import nextcord
from nextcord.ext import commands, ipc
from nextcord import Interaction, SlashOption
import os
from utils import variables

class VALcord(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.getenv("BETA_MODE"):
            self.ipc = ipc.Server(self, host=os.getenv("IPC_HOST", "localhost"), secret_key=variables.IPC_SECRET)

intents = nextcord.Intents.default()
intents.members = True
bot = VALcord(intents=intents)

excluded_cogs = []
beta_excluded_cogs = ["status.py", "ipc.py", "votes.py"]
loadedCogs = []

# Loads Cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        if filename not in excluded_cogs:
            # Check if the file is 'status.py' and if 'BETA_MODE' is set to 'true'
            if (filename in beta_excluded_cogs) and os.getenv("BETA_MODE"):
                continue  # Skip loading 'status.py' if BETA_MODE is true

            try:
                # Load the cog
                bot.load_extension(f"cogs.{filename[:-3]}")
                loadedCogs.append(filename[:-3])
            except Exception as e:
                print(f"Error loading {filename[:-3]}: {e}")

### Cog Management Commands
@bot.slash_command(name="cog-load", description="Loads a cog", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
async def cog_load(interaction: Interaction, cog: str, task: bool = SlashOption("istask", description="Is this a task cog?", required=False, default=False)):
    try:
        if task:
            bot.load_extension(f"cogs.tasks.{cog}")
        else:
            bot.load_extension(f"cogs.{cog}")
        await interaction.response.send_message(f"Loaded {cog}")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

@bot.slash_command(name="cog-unload", description="Unloads a cog", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
async def cog_unload(interaction: Interaction, cog: str, task: bool = SlashOption("istask", description="Is this a task cog?", required=False, default=False)):
    try:
        if task:
            bot.unload_extension(f"cogs.tasks.{cog}")
        else:
            bot.unload_extension(f"cogs.{cog}")
        await interaction.response.send_message(f"Unloaded {cog}")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

@bot.slash_command(name="cog-reload", description="Reloads a cog", guild_ids=variables.DEVELOPER_GUILD_IDS, default_member_permissions=nextcord.Permissions(administrator=True))
async def cog_reload(interaction: Interaction, cog: str, task: bool = SlashOption("istask", description="Is this a task cog?", required=False, default=False)):
    try:
        if task:
            bot.reload_extension(f"cogs.tasks.{cog}")
        else:
            bot.reload_extension(f"cogs.{cog}")
        await interaction.response.send_message(f"Reloaded {cog}")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

### Start the bot
if __name__ == "__main__":
    if not os.getenv("BETA_MODE"):
        bot.ipc.start()
    bot.run(variables.BETA_DISCORD_TOKEN if os.getenv("BETA_MODE") else variables.VALCORD_DISCORD_TOKEN)