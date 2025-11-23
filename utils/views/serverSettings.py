import nextcord
from .. import colors


def create_server_settings_embed(server_data, og_interaction):
    embed = nextcord.Embed(title="Server Settings", color=colors.primary)
    embed.set_author(name=og_interaction.guild.name, icon_url=og_interaction.guild.icon.url)
    embed.add_field(name="Log Channel", value=server_data["log_channel"], inline=False)
    embed.add_field(name="News",
                    value=f"**Enabled:** {server_data['news']}\n**Channel:** {server_data['news_channel']}",
                    inline=False)
    embed.add_field(name="Patch Notes",
                    value=f"**Enabled:** {server_data['patch_notes']}\n**Channel:** {server_data['patch_notes_channel']}",
                    inline=False)
    embed.add_field(name="Linked Roles", value=f"_Coming Soon_", inline=False)
    return embed


class NewsSettingsView(nextcord.ui.View):
    def __init__(self, og_interaction: nextcord.Interaction, server_data):
        super().__init__()
        self.og_interaction = og_interaction
        self.server_data = server_data

    @nextcord.ui.button(label="Enable", style=nextcord.ButtonStyle.green)
    async def toggle_news(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(label="Back", style=nextcord.ButtonStyle.grey)
    async def back_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = create_server_settings_embed(self.server_data, self.og_interaction)
        view = ServerSettingsView(self.og_interaction, self.server_data)
        return await self.og_interaction.edit_original_message(embed=embed, view=view)

class ServerSettingsView(nextcord.ui.View):
    def __init__(self, og_interaction: nextcord.Interaction, server_data):
        super().__init__()
        self.og_interaction = og_interaction
        self.server_data = server_data

    @nextcord.ui.button(label="News Settings", style=nextcord.ButtonStyle.primary)
    async def news_settings(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = NewsSettingsView(self.og_interaction, self.server_data)
        return await self.og_interaction.edit_original_message(view=view)

    @nextcord.ui.button(label="Patch Notes Settings", style=nextcord.ButtonStyle.primary)
    async def patch_notes_settings(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    async def on_timeout(self, interaction: nextcord.Interaction):
        return await self.og_interaction.delete_original_message()