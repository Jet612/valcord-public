import nextcord

class PatchAndNewsView(nextcord.ui.View):
	def __init__(self, url, title):
		super().__init__()
		self.add_item(nextcord.ui.Button(label=title, url=url, style=nextcord.ButtonStyle.url))