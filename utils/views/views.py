import nextcord

class LinkAccountView(nextcord.ui.View):
    def __init__(self, uuid: str):
        super().__init__()
        self.uuid = uuid
        self.add_item(nextcord.ui.Button(label="Link Account", url=f"https://valcord.xyz/link-riot-account?state={self.uuid}"))

class InviteView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(nextcord.ui.Button(label="Invite VALcord", url="https://valcord.xyz/invite"))