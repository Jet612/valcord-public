import nextcord
from . import views
from .. import colors
from .. import database
from typing import Union

users_db = database.Users()

def create_account_settings_embed(interaction: nextcord.Interaction, user_data: dict, account_data: Union[dict, None]):
    embed = nextcord.Embed(color=colors.primary)
    if interaction.user.avatar is not None:
        embed.set_author(name=f"{interaction.user.name} | Account Settings", icon_url=interaction.user.avatar.url)
    else:
        embed.set_author(name=f"{interaction.user.name} | Account Settings")
    if user_data["api_puuid"] is None:
        embed.add_field(name="Riot Games Account", value="```No account linked```", inline=False)
    else:
        embed.add_field(name="Riot Games Account", value=f"```{account_data.gameName}#{account_data.tagLine}```", inline=False)
    embed.add_field(name="Private Account", value=f"```{user_data['private']}```", inline=False)
    return embed

class UnlinkedView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, user_Data: dict, account_data: Union[dict, None]):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.user_data = user_Data
        self.account_data = account_data

    @nextcord.ui.button(label="Back", style=nextcord.ButtonStyle.secondary)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = create_account_settings_embed(self.ogInteraction, self.user_data, self.account_data)
        view = AccountSettingsView(self.ogInteraction, self.user_data, self.account_data)
        await view.update_buttons()
        await self.ogInteraction.edit_original_message(embed=embed, view=view)

class UnlinkConfirmatinoView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, user_data: dict, account_data: Union[dict, None]):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.user_data = user_data
        self.account_data = account_data

    @nextcord.ui.button(label="Yes, unlink", style=nextcord.ButtonStyle.success)
    async def yes_unlink(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        users_db.update_user({"uuid": self.user_data["uuid"]}, {"api_puuid": None, "access_token": None, "refresh_token": None})
        self.user_data = users_db.get_user({"uuid": self.user_data["uuid"]})
        embed = nextcord.Embed(title="Riot Games Account Unlinked", description="Your Riot Games account has been successfully unlinked from your Discord account.", color=colors.primary)
        view = UnlinkedView(self.ogInteraction, self.user_data, self.account_data)
        await self.ogInteraction.edit_original_message(embed=embed, view=view)

    @nextcord.ui.button(label="No, cancel", style=nextcord.ButtonStyle.danger)
    async def no_cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = create_account_settings_embed(self.ogInteraction, self.user_data, self.account_data)
        view = AccountSettingsView(self.ogInteraction, self.user_data, self.account_data)
        await view.update_buttons()
        await self.ogInteraction.edit_original_message(embed=embed, view=view)

class AccountSettingsView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, user_data: dict, account_data: Union[dict, None]):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.user_data = user_data
        self.account_data = account_data
        
    @nextcord.ui.button(label="Riot Games Account", style=nextcord.ButtonStyle.secondary)
    async def riot_games_account(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if button.label == "Link Riot Games Account":
            view = views.LinkAccountView(self.user_data["uuid"])
            embed = nextcord.Embed(title="Link Riot Games Account", description="Click on the `Link Account` button below to link your Riot Games account.", color=colors.primary)
            embed.set_footer(text="This link contains sensitive information. Do not share it with anyone.")
            await self.ogInteraction.edit_original_message(embed=embed, view=view)
        elif button.label == "Unlink Riot Games Account":
            embed = nextcord.Embed(title="Unlink Riot Games Account", description=f"Are you sure you want to unlink your Riot Games account (`{self.account_data.gameName}#{self.account_data.tagLine}`)?", color=colors.primary)
            view = UnlinkConfirmatinoView(self.ogInteraction, self.user_data, self.account_data)
            await self.ogInteraction.edit_original_message(embed=embed, view=view)

    @nextcord.ui.button(label="Toggle Privacy", style=nextcord.ButtonStyle.secondary)
    async def private_account(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if button.label == "Toggle Privacy":
            if self.user_data["private"] == True:
                users_db.update_user({"uuid": self.user_data["uuid"]}, {"private": False})
                self.user_data = users_db.get_user({"uuid": self.user_data["uuid"]})
                embed = create_account_settings_embed(self.ogInteraction, self.user_data, self.account_data)
                await self.ogInteraction.edit_original_message(embed=embed)
            else:
                users_db.update_user({"uuid": self.user_data["uuid"]}, {"private": True})
                self.user_data = users_db.get_user({"uuid": self.user_data["uuid"]})
                embed = create_account_settings_embed(self.ogInteraction, self.user_data, self.account_data)
                await self.ogInteraction.edit_original_message(embed=embed)

    async def update_buttons(self):
        if self.user_data["api_puuid"] is None:
            self.children[0].label = "Link Riot Games Account"
        else:
            self.children[0].label = "Unlink Riot Games Account"


