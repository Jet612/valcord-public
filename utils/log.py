import nextcord
from nextcord.ext import commands
import inspect
from functools import wraps

import os

log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))

def log_command(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the function name
        function_name = func.__name__
        
        # Get the arguments passed to the function
        arguments = inspect.signature(func).bind(*args, **kwargs).arguments

        # Retrieve the bot instance from args
        self = args[0]
        bot: commands.Bot = self.bot

        interaction: nextcord.Interaction = args[1]

        # Create the log message
        embed = nextcord.Embed(title=f"/{interaction.application_command.qualified_name}")
        embed.add_field(name="User", value=f"```{interaction.user.id}``` ({interaction.user.name})", inline=False)
        embed.add_field(name="Guild", value=f"```{interaction.guild.id}``` ({interaction.guild.name})", inline=False)
        embed.add_field(name="Interaction ID", value=f"```{interaction.id}```", inline=False)
        formatted_arguments = '\n'.join([f'{key}: {value}' for key, value in arguments.items()])
        embed.add_field(name="Arguments", value=f"```{formatted_arguments}```", inline=False)
        
        # Send the log message to the specified Discord channel
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        # Call the original command function
        return await func(*args, **kwargs)
    
    return wrapper
