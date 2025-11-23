import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from utils import colors, Users, views, variables
import valaw

users_db = Users()
client = valaw.Client(variables.RIOT_API_KEY, cluster="americas")

class AccountCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="link-account", description="Link your Riot Games account to your Discord account")
    async def link_account(self, interaction: Interaction):
        db_user_data = users_db.get_user({"user_id": interaction.user.id})
        
        # If the user is not in the database, create a new user
        if db_user_data is None:
            users_db.create_user(interaction.user.id)
            db_user_data = users_db.get_user({"user_id": interaction.user.id})

        # If the user has already linked their account, send an error message
        elif db_user_data["api_puuid"] is not None:
            account_data = await client.GET_getByPuuid(db_user_data["api_puuid"])
            embed = nextcord.Embed(title="Link Riot Games Account", description=f"A Riot Games account is already linked (`{account_data.gameName}#{account_data.tagLine}`).\n\nTo connect a different account use </account-settings:1214957391137738834>.", color=colors.primary)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = nextcord.Embed(title="Link Riot Games Account", description="Click on the `Link Account` button below to link your Riot Games account.", color=colors.primary)
        embed.set_footer(text="This link contains sensitive information. Do not share it with anyone.")
        view = views.LinkAccountView(db_user_data["uuid"])
        return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.slash_command(name="account-settings", description="View your account settings")
    async def account_settings(self, interaction: Interaction):
        db_user_data = users_db.get_user({"user_id": interaction.user.id})

        # If the user is not in the database, create a new user
        if db_user_data is None:
            users_db.create_user(interaction.user.id)
            db_user_data = users_db.get_user({"user_id": interaction.user.id})
        embed = nextcord.Embed(color=colors.primary)
        if interaction.user.avatar is not None:
            embed.set_author(name=f"{interaction.user.name} | Account Settings", icon_url=interaction.user.avatar.url)
        else:
            embed.set_author(name=f"{interaction.user.name} | Account Settings")
        if db_user_data["api_puuid"] is None:
            embed.add_field(name="Riot Games Account", value="```No account linked```", inline=False)
            account_data = None
        else:
            account_data = await client.GET_getByPuuid(db_user_data["api_puuid"])
            embed.add_field(name="Riot Games Account", value=f"```{account_data.gameName}#{account_data.tagLine}```", inline=True)
        embed.add_field(name="Private Account", value=f"```{db_user_data['private']}```", inline=False)
        view = views.AccountSettingsView(interaction, db_user_data, account_data)
        await view.update_buttons()
        return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(AccountCog(bot))