import nextcord
from .. import colors

class HelpDropdown(nextcord.ui.Select):
    def __init__(self, ogInteraction: nextcord.Interaction):
        self.ogInteraction = ogInteraction
        options = [
            nextcord.SelectOption(label="Statistics", description="VALORANT Statistics", value="statistics"),
            nextcord.SelectOption(label="Account", description="Commands related to your account", value="account"),
            nextcord.SelectOption(label="News/Patch Notes", description="Latest News and Patch Notes", value="news"),
            nextcord.SelectOption(label="Utilities", description="Utility and miscellaneous commands", value="utilities")
        ]
        super().__init__(placeholder="Select a category", options=options)

    async def callback(self, interaction: nextcord.Interaction):
        if self.values[0] == "statistics":
            embed = nextcord.Embed(title="Statistics Commands", description="Commands related to VALORANT statistics", color=colors.primary)
            embed.add_field(name="</stats:1238205493869281310>", value="View a user's VALORANT statistics", inline=False)
            embed.add_field(name="</agent:1238205496570286180>", value="View information about a VALORANT agent", inline=False)
            embed.add_field(name="</weapon:1238205500370321499>", value="View information about a VALORANT weapon", inline=False)
            embed.add_field(name="</skin:1238219314490904760>", value="View information about a VALORANT weapon skin", inline=False)
            await self.ogInteraction.edit_original_message(embed=embed)
        elif self.values[0] == "account":
            embed = nextcord.Embed(title="Account Commands", description="Commands related to your account", color=colors.primary)
            embed.add_field(name="</account-settings:1214957391137738834>", value="View your account settings", inline=False)
            embed.add_field(name="</link-account:1022698591749423205>", value="Link your Riot Games account to your Discord account", inline=False)
            await self.ogInteraction.edit_original_message(embed=embed)
        elif self.values[0] == "news":
            embed = nextcord.Embed(title="News/Patch Notes Commands", description="Latest News and Patch Notes", color=colors.primary)
            embed.add_field(name="</patch-notes:1239064784251387904>", value="Get the latest patch notes", inline=False)
            embed.add_field(name="</news:1239071320705335346>", value="Get the latest news", inline=False)
            await self.ogInteraction.edit_original_message(embed=embed)
        elif self.values[0] == "utilities":
            embed = nextcord.Embed(title="Utilities Commands", description="Utility and miscellaneous commands", color=colors.primary)
            embed.add_field(name="</help:1214957386515877889>", value="View a list of commands", inline=False)
            embed.add_field(name="</ping:1217492969339359273>", value="Pong!", inline=False)
            embed.add_field(name="</invite:1217492974280114236>", value="Invite VALcord to your server", inline=False)
            embed.add_field(name="</report-bug:1217492975832006728>", value="Report a bug", inline=False)
            embed.add_field(name="</info:1217492978424348682>", value="View information/links about VALcord", inline=False)
            await self.ogInteraction.edit_original_message(embed=embed)

class HelpView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.add_item(HelpDropdown(ogInteraction))