import nextcord
from .. import database

votes_collection = database.Votes()

class VoteReminderView(nextcord.ui.View):
    def __init__(self, user_id: int, reminders: bool, og_message: nextcord.Message):
        super().__init__(timeout=None)
        self.user_id = int(user_id)
        self.reminders = reminders
        self.ogMessage = og_message
    
    @nextcord.ui.button(label="Reminders", style=nextcord.ButtonStyle.grey)
    async def vote_again(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self.user_id:
            if button.label == "Get Reminders":
                votes_collection.update_user({"user_id": self.user_id}, {"remind": True})
                await self.update_button()
            else:
                votes_collection.update_user({"user_id": self.user_id}, {"remind": False})
                await self.update_button()

    async def update_button(self):
        if self.children[0].label == "Reminders":
            if self.reminders["remind"]:
                self.children[0].label = "Unsubscribe from reminders"
                self.children[0].style = nextcord.ButtonStyle.red
            else:
                self.children[0].label = "Get Reminders"
                self.children[0].style = nextcord.ButtonStyle.green
        else:
            if self.children[0].label == "Get Reminders":
                self.children[0].label = "Unsubscribe from reminders"
                self.children[0].style = nextcord.ButtonStyle.red
            else:
                self.children[0].label = "Get Reminders"
                self.children[0].style = nextcord.ButtonStyle.green
        await self.ogMessage.edit(view=self)