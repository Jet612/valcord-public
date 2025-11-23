import nextcord
from typing import List
from .. import database, colors, images
import valaw
from datetime import datetime

valorantInfo_db = database.ValorantInfo()

class PlayerSelectView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, match_list: List[valaw.objects.MatchDto], puuid: str):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.match_list = match_list
        self.puuid = puuid

    @nextcord.ui.button(label="Back", style=nextcord.ButtonStyle.grey)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id == self.ogInteraction.user.id:
            view = StatsView(self.ogInteraction, self.match_list, self.puuid)
            await view.update_embed()
            await self.ogInteraction.edit_original_message(view=view)
        

class SelectGame(nextcord.ui.Select):
    def __init__(self, ogInteraction: nextcord.Interaction, match_list: List[valaw.objects.MatchDto], puuid: str):
        self.ogInteraction = ogInteraction
        self.match_list = match_list
        self.puuid = puuid
        options = []
        match_index = -1
        for match in match_list:
            match_index += 1
            if match_index >= 25:
                break
            for player in match.players:
                if player.puuid == self.puuid:
                    player = player
                    break
            player_team = player.teamId
            team1_score = 0
            team2_score = 0
            for team in match.teams:
                if team.teamId == player_team:
                    team1_score = team.roundsWon
                else:
                    team2_score = team.roundsWon
            map = valorantInfo_db.get_info("map_path_to_name")['data'].get(match.matchInfo.mapId)
            mode = match.matchInfo.queueId
            gameStartMillis = match.matchInfo.gameStartMillis
            gameStart = datetime.fromtimestamp(int((gameStartMillis/1000)-18000))
            time = gameStart.strftime("%m/%d/%Y, %H:%M")
            kills = player.stats.kills
            deaths = player.stats.deaths
            assists = player.stats.assists
            agent = valorantInfo_db.get_info("character_id_to_name")['data'].get(str(player.characterId).upper())
            icon = valorantInfo_db.get_info("gamemode_emojis_by_asset_path")['data'].get(match.matchInfo.gameMode)
            options.append(nextcord.SelectOption(label=f"{kills}/{deaths}/{assists} | {agent} | {team1_score}-{team2_score}", description=f'{mode} | {map} | {time} EST', emoji=icon, value=match_index))
        super().__init__(placeholder="Select a match", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.user == self.ogInteraction.user:
            match = self.match_list[int(self.values[0])]
            self.disabled = True
            await self.ogInteraction.edit_original_message(view=self.view)
            tied = False
            if match.teams[0].won == False and match.teams[1].won == False:
                tied = True
            blueTeam = f'{"Name#Tag" : <22} | Score | {"K/D/A" : <8} | Agent\n{"" :-<53}'
            redTeam = f'{"Name#Tag" : <22} | Score | {"K/D/A" : <8} | Agent\n{"" :-<53}'
            blueTeamList = []
            redTeamList = []
            for player in match.players:
                playerGameName = player.gameName
                playerTagLine = player.tagLine
                playerName = f"{playerGameName}#{playerTagLine}"
                playerStats = player.stats
                playerKills = str(playerStats.kills).zfill(2)
                playerDeaths = str(playerStats.deaths).zfill(2)
                playerAssists = str(playerStats.assists).zfill(2)
                playerScore = playerStats.score
                playerAgent = valorantInfo_db.get_info("character_id_to_name")['data'].get(player.characterId.upper())
                playerStr = f'{playerName : <22} | {playerScore : <5} | {playerKills}/{playerDeaths}/{playerAssists} | {playerAgent}'
                map = valorantInfo_db.get_info("map_path_to_name")['data'].get(match.matchInfo.mapId)
                mode = match.matchInfo.queueId
                matchStartTime = match.matchInfo.gameStartMillis
                matchStartTime = matchStartTime/1000
                matchStartTime = int(matchStartTime)
                if player.teamId == "Blue":
                    blueTeamList.append(playerStr)
                elif player.teamId == "Red":
                    redTeamList.append(playerStr)
            blueTeamList.sort(key=lambda x: int(x[25:29]), reverse=True)
            redTeamList.sort(key=lambda x: int(x[25:29]), reverse=True)
            for player in blueTeamList:
                blueTeam += f'\n{player}'
            for player in redTeamList:
                redTeam += f'\n{player}'
            teams = match.teams
            for team in teams:
                if team.teamId == "Red":
                    redTeamScore = team.roundsWon
                elif team.teamId == "Blue":
                    blueTeamScore = team.roundsWon
            embed = nextcord.Embed(title=f"{map} | {mode}", description=f"<t:{matchStartTime}>", color=colors.primary)
            embed.add_field(name=f"Blue Team - {blueTeamScore}", value=f"```{blueTeam}```", inline=False)
            embed.add_field(name=f"Red Team - {redTeamScore}", value=f"```{redTeam}```", inline=False)
            view = PlayerSelectView(self.ogInteraction, self.match_list, self.puuid)
            await self.ogInteraction.edit_original_message(attachments=[], embed=embed, view=view)


class StatsView(nextcord.ui.View):
    def __init__(self, ogInteraction: nextcord.Interaction, match_list: List[valaw.objects.MatchDto], puuid: str):
        super().__init__()
        self.ogInteraction = ogInteraction
        self.match_list = match_list
        self.puuid = puuid
        self.current_screen = 'overview'  # Initial screen

    @nextcord.ui.button(label="Overview", style=nextcord.ButtonStyle.blurple, disabled=True)
    async def overview(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.change_screen('overview')

    @nextcord.ui.button(label="Matches", style=nextcord.ButtonStyle.grey)
    async def matches(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.change_screen('matches')

    async def update_embed(self, screen=None):
        if screen is None or screen == "overview":
            await self.ogInteraction.edit_original_message(content=None, embed=None, file=nextcord.File(f"statistics_images/overview/{self.puuid}.png"))
        else:
            await self.ogInteraction.edit_original_message(content=None, embed=None, file=nextcord.File(f"statistics_images/matches/{self.puuid}.png"))
            #embed = nextcord.Embed(title="Matches", description="This page is coming soon!", color=colors.primary)
            #await self.ogInteraction.edit_original_message(content=None, embed=embed, files=[])

    async def update_buttons(self):
        for item in self.children:
            if isinstance(item, nextcord.ui.Button):
                if item.label.lower() == self.current_screen:
                    item.style = nextcord.ButtonStyle.blurple
                    item.disabled = True
                else:
                    item.style = nextcord.ButtonStyle.grey
                    item.disabled = False
        await self.ogInteraction.edit_original_message(view=self)

    async def change_screen(self, screen):
        self.current_screen = screen
        await self.update_buttons()
        await self.update_embed(screen=screen)

