import nextcord
from .. import colors

class SkinView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, skin_data: dict):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.skin_data = skin_data

        self.add_item(ChromaDropdown(ogInteraction, skin_data))

class ChromaDropdown(nextcord.ui.Select):
    def __init__(self, ogInteraction: nextcord.Interaction, skin_data: dict):
        self.ogInteraction = ogInteraction
        self.skin_data = skin_data
        options = []
        for chroma in skin_data['chromas']:
            options.append(nextcord.SelectOption(label=chroma['displayName'], value=chroma['uuid']))

        super().__init__(placeholder="Select a Chroma", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user == self.ogInteraction.user:
            chroma_id = self.values[0]
            chroma = [chroma for chroma in self.skin_data['chromas'] if chroma['uuid'] == chroma_id][0]
            embed = nextcord.Embed(title=f"{chroma['displayName']}", color=colors.primary)
            embed.set_image(url=chroma['fullRender'])
            await self.ogInteraction.edit_original_message(embed=embed)