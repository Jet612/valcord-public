import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import os
from utils import colors, views

class UtilitiesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="View a list of commands")
    async def help(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Help | VALcord Commands", description=f"**Notice**: {self.bot.user.mention} is currently undergoing a remodel for V2. Commands may not work as intended!", color=colors.primary)
        view = views.HelpView(interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @nextcord.slash_command(name="ping", description="Pong!")
    async def ping(self, interaction: nextcord.Interaction):
        latency = round(self.bot.latency * 1000)
        if latency <= 50:
            footer_text = "🟢 | Status: Good"
        elif latency <= 80:
            footer_text = "🟡 | Status: Fair"
        else:
            footer_text = "🔴 | Status: Poor"
        embed = nextcord.Embed(title="Ping", description=f"Latency: {latency}ms", color=colors.primary)
        embed.set_footer(text=footer_text)
        return await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="invite", description="Invite VALcord to your server")
    async def invite(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Add VALcord to your server", description=f"{self.bot.user.mention} lets you see VALORANT statistics from the comfort of Discord. Want to add it to your own server?", color=colors.primary)
        embed.set_author(name="VALcord", icon_url=self.bot.user.avatar.url)
        view = views.views.InviteView()
        return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.slash_command(name="report-bug", description="Report a bug")
    async def bug_report(self, interaction: nextcord.Interaction, bug: str = SlashOption(description="The bug you are reporting", required=True)):
        embed = nextcord.Embed(description=f"{bug}", color=colors.primary)
        embed.set_author(name=f"{interaction.user} - {interaction.user.id}", icon_url=interaction.user.avatar.url)
        await self.bot.get_channel(int(os.getenv("BUG_REPORT_CHANNEL_ID", "0"))).send(embed=embed)
        embed2 = nextcord.Embed(description="Your report has been sent to the developers!", color=colors.primary)
        return await interaction.response.send_message(embed=embed2, ephemeral=True)

    @nextcord.slash_command(name="info", description="View information/links about VALcord")
    async def info(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="VALcord Information", description="VALcord is a Discord bot that lets you see VALORANT statistics from the comfort of Discord. It is currently undergoing a remodel for V2. Commands may not work as intended!", color=colors.primary)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds)}`", inline=False)
        embed.add_field(name="Links", value=f"Website: [valcord.xyz](https://valcord.xyz)\nSupport Server: [Discord](https://valcord.xyz/support)\nInvite: [Invite VALcord](https://valcord.xyz/invite)\nVote: [top.gg](https://top.gg/bot/{os.getenv('BOT_ID', '0')})", inline=False)
        embed.set_footer(text=f"VALcord | ID: {self.bot.user.id}")

        return await interaction.response.send_message(embed=embed, ephemeral=True)




def setup(bot):
    bot.add_cog(UtilitiesCog(bot))