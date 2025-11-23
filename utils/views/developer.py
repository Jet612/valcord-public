import nextcord

class SendMessageView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, users: list, embed: nextcord.Embed):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.users = users
        self.embed = embed

    @nextcord.ui.button(label="Yes, Send", style=nextcord.ButtonStyle.success)
    async def send_message(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        failed_users = []
        for user in self.users:
            try:
                await user.send(embed=self.embed)
            except nextcord.Forbidden:
                failed_users.append(user.mention)
        
        if failed_users:
            failed_mentions = " ".join(failed_users)
            await self.ogInteraction.edit_original_message(embed=None, view=None, content=f"Failed to send message to: {failed_mentions}")
        else:
            await self.ogInteraction.edit_original_message(embed=None, view=None, content="Message sent to all users.")

    @nextcord.ui.button(label="No, Cancel", style=nextcord.ButtonStyle.danger)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.ogInteraction.edit_original_message(embed=None, view=None, content="Message cancelled.")

# Create bot instance and add the cog