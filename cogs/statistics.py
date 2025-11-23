import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from utils import colors, variables, database, valorantAPI, views, images, log_command, valorant_handler
import valaw
import Levenshtein
from datetime import datetime

users_db = database.Users()
valorantInfo_db = database.ValorantInfo()
stats_db = database.RiotAPICollection()
characters = valorantInfo_db.get_info("characters")['data']
characters.remove("Null UI Data!")
weapons = valorantInfo_db.get_info("weapons")['data']
maps = valorantInfo_db.get_info("maps")['data']
skin_names = valorantInfo_db.get_info("skin_names")['data']
skin_name_to_id = valorantInfo_db.get_info("skin_name_to_id")['data']
skin_id_to_data = valorantInfo_db.get_info("skin_id_to_data")['data']
valawClient = valaw.Client(variables.RIOT_API_KEY, cluster="americas")


class StatisticsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="stats", description="View a user's VALORANT statistics")
    @log_command
    async def stats(self, interaction: nextcord.Interaction, riot_id: str = SlashOption(name="riot-id", description="The Riot ID of the user (username#tagline)", required=False)):
        # Initialization
        current_season = valorantInfo_db.get_info("current_season")['data']
        season_id = current_season.get("act_id")

        # Check if riot_id is provided or user has linked account
        if riot_id is None:
            db_user_data = users_db.get_user({"user_id": interaction.user.id})
            if db_user_data is None or db_user_data.get("api_puuid") is None:
                embed = nextcord.Embed(
                    description="You did not specify a Riot ID and do not have a Riot Games account linked. Please specify a Riot ID or link your account.",
                    color=colors.primary)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            api_puuid = db_user_data["api_puuid"]
            riot_id = db_user_data.get("riot_id")
            ephemeral = db_user_data["private"]
        else:
            # Validate Riot ID
            riot_id_split = riot_id.split("#")
            if len(riot_id_split) != 2:
                embed = nextcord.Embed(
                    description="Invalid Riot ID. Please specify a valid Riot ID (username#tagline).",
                    color=colors.primary)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            riot_id_username = riot_id_split[0]
            riot_id_tagline = riot_id_split[1]
            try:
                riot_account_data = await valawClient.GET_getByRiotId(riot_id_username, riot_id_tagline)
            except valaw.Exceptions.RiotAPIResponseError as e:
                if e.status_code == 404:
                    embed = nextcord.Embed(description=f"No player found with Riot ID `{riot_id}`",
                                           color=colors.primary)
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    raise e
            api_puuid = riot_account_data.puuid
            riot_id = f"{riot_account_data.gameName}#{riot_account_data.tagLine}"
            db_user_data = users_db.get_user({"api_puuid": api_puuid})
            if db_user_data is not None and db_user_data.get("private") is True:
                embed = nextcord.Embed(description=f"`{riot_id}` user has set their account to private.",
                                       color=colors.primary)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            ephemeral = False

        embed = nextcord.Embed(description="Fetching statistics...", color=colors.primary)
        embed.set_footer(
            text="Please wait while we calculate the statistics. The more matches played, the longer this will take.")
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

        # Check if statistics are already cached in the database
        cached_stats = stats_db.get_users_act_stats(api_puuid, season_id)

        if cached_stats:
            stats = cached_stats["statistics"]
            matches_played_ids = set(stats["matches_played_ids"])
        else:
            stats = {
                "matches_played": 0,
                "matches_played_ids": [],
                "rank": 0,
                "tier": 0,
                "level": 0,
                "kd_ratio": 0,
                "win_percentage": 0,
                "average_combat_score": 0,
                "headshot_percentage": 0,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "kda_ratio": 0,
                "damage_per_round": 0,
                "wins": 0,
                "losses": 0,
                "ties": 0,
                "first_bloods": 0,
                "aces": 0,
                "most_kills": 0,
                "shots_hit": 0,
                "shots_head": 0,
                "shots_body": 0,
                "shots_legs": 0,
                "damage_total": 0,
                "abilities_used": 0,
                "characters_played": [],
                "last_updated": 0,
                "acs_total": 0,
                "rounds_played": 0,
                "latest_match_timestamp": 0,
                "season_display_name": current_season.get("episode_name") + " : " + current_season.get("act_name"),
                "season_id": current_season.get("act_id")
            }
            matches_played_ids = set()

        # Calculate statistics if not cached or if there are new matches
        shard_data = await valawClient.GET_getActiveShard(api_puuid)
        matches = await valawClient.GET_getMatchlist(api_puuid, shard_data.activeShard)
        stats_db.add_matchlist(matches)

        new_matches = 0
        matches_list = []

        for match in matches.history:
            if match.queueId == "competitive":
                # Check if the match has already been counted, if so, skip it
                custom_match = stats_db.get_custom_match(api_puuid, match.matchId)
                if match.matchId in matches_played_ids and custom_match is not None:
                    continue
                # Get the match data
                match_data = await valorant_handler.get_match(match.matchId, shard_data.activeShard)
                # Check if the match is from the current season, if not, stop counting matches
                if match_data.matchInfo.seasonId != season_id:
                    break

                new_matches += 1
                stats["matches_played"] += 1 # Increment matches played
                matches_list.append(match_data) # Add match to list of matches played
                matches_played_ids.add(match.matchId)  # Add match ID to set of matches played
                custom_data = {
                    "outcome": "",
                    "agent_uuid": "",
                    "map": "",
                    "rank": "",
                    "kda": "",
                    "user-score": "",
                    "game-score": "",
                    "season_id": match_data.matchInfo.seasonId
                }


                for player in match_data.players:
                    if player.puuid == api_puuid:
                        if stats["latest_match_timestamp"] < match_data.matchInfo.gameStartMillis:
                            stats["latest_match_timestamp"] = match_data.matchInfo.gameStartMillis
                            stats["tier"] = player.competitiveTier
                            stats["level"] = player.accountLevel
                        custom_data["rank"] = valorantInfo_db.get_info("rank_dictionary_by_ids")['data'].get(str(player.competitiveTier))

                        stats["kills"] += player.stats.kills
                        stats["deaths"] += player.stats.deaths
                        stats["assists"] += player.stats.assists
                        custom_data["kda"] = f"{player.stats.kills}/{player.stats.deaths}/{player.stats.assists}"
                        custom_data["user-score"] = player.stats.score
                        stats["acs_total"] += player.stats.score / player.stats.roundsPlayed
                        stats["rounds_played"] += player.stats.roundsPlayed
                        stats["most_kills"] = max(stats["most_kills"], player.stats.kills)
                        for roundResult in match_data.roundResults:
                            first_blood_id = ""
                            first_blood_time = 0
                            for player_round in roundResult.playerStats:
                                if player_round.puuid == api_puuid:
                                    for damage in player_round.damage:
                                        stats["shots_hit"] += damage.bodyshots + damage.headshots + damage.legshots
                                        stats["shots_head"] += damage.headshots
                                        stats["shots_body"] += damage.bodyshots
                                        stats["shots_legs"] += damage.legshots
                                        stats["damage_total"] += damage.damage
                                for kill in player_round.kills:
                                    if kill.timeSinceRoundStartMillis < first_blood_time or first_blood_time == 0:
                                        first_blood_time = kill.timeSinceRoundStartMillis
                                        first_blood_id = player_round.puuid
                                if player_round.puuid == api_puuid and len(player_round.kills) == 5:
                                    stats["aces"] += 1
                            if first_blood_id == api_puuid:
                                stats["first_bloods"] += 1

                        for team in match_data.teams:
                            if team.teamId == player.teamId:
                                team_score = team.roundsWon
                                if team.won:
                                    stats["wins"] += 1
                                    custom_data["outcome"] = "win"
                                else:
                                    if match_data.teams[0].won != match_data.teams[1].won:
                                        stats["losses"] += 1
                                        custom_data["outcome"] = "lost"
                                    else:
                                        stats["ties"] += 1
                                        custom_data["outcome"] = "tie"
                            else:
                                enemy_score = team.roundsWon
                        custom_data["game-score"] = f"{team_score}-{enemy_score}"
                                
                        stats["characters_played"].append(player.characterId)
                        custom_data["agent_uuid"] = player.characterId
                        if player.stats.abilityCasts is not None:
                            stats["abilities_used"] += (
                                    player.stats.abilityCasts.grenadeCasts +
                                    player.stats.abilityCasts.ability1Casts +
                                    player.stats.abilityCasts.ability2Casts +
                                    player.stats.abilityCasts.ultimateCasts
                            )
                        custom_data["map"] = valorantInfo_db.get_info("map_path_to_name")['data'].get(match_data.matchInfo.mapId)
                        stats_db.update_custom_match(api_puuid, match.matchId, custom_data)
                        break


        if stats["matches_played"] == 0:
            embed = nextcord.Embed(description=f"No competitive matches found for `{riot_id}` in {current_season.get('episode_name')} : {current_season.get('act_name')}",
                                   color=colors.primary)
            return await interaction.edit_original_message(embed=embed)

        # Calculate statistics if there are new matches
        if new_matches > 0:
            if stats["deaths"] == 0:
                stats["kd_ratio"] = stats["kills"]
                stats["kda_ratio"] = stats["kills"] + stats["assists"]
            else:
                stats["kd_ratio"] = "{:.2f}".format(stats["kills"] / stats["deaths"])
                kills_plus_assists = stats["kills"] + stats["assists"]
                stats["kda_ratio"] = "{:.2f}".format(kills_plus_assists / stats["deaths"])

            stats["win_percentage"] = "{:.1f}".format((stats["wins"] / stats["matches_played"]) * 100)
            # most_played_agent = max(set(stats["characters_played"]), key=stats["characters_played"].count)
            # stats["most_played_agent_name"] = valorantInfo_db.get_info("character_id_to_name")['data'].get(
            #     str(most_played_agent).upper())
            stats["rank"] = valorantInfo_db.get_info("rank_dictionary_by_ids")['data'].get(str(stats["tier"]))
            stats["headshot_percentage"] = "{:.1f}".format((stats["shots_head"] / stats["shots_hit"]) * 100)
            stats["average_combat_score"] = "{:.1f}".format(stats["acs_total"] / stats["matches_played"])
            stats["damage_per_round"] = "{:.1f}".format(stats["damage_total"] / stats["rounds_played"])

        # Convert the set back to a list before saving to the database
        stats["matches_played_ids"] = list(matches_played_ids)

        # Save the statistics in the database
        stats_db.update_user_stats(api_puuid, season_id, stats)

        user_data = await valawClient.GET_getByPuuid(api_puuid)
        riot_id = f"{user_data.gameName}#{user_data.tagLine}"

        # Create the statistics image
        images.create_overview_statistics_image(
            riot_id,
            stats,
            f"{api_puuid}"
        )

        full_matchlist = stats_db.get_matchlist(api_puuid)
        last_5_matches = []
        for match in full_matchlist.history:
            if len(last_5_matches) == 5:
                break
            if match.queueId == "competitive":
                match_data = stats_db.get_custom_match(api_puuid, match.matchId)
                if match_data is not None:
                    if match_data["data"]["season_id"] == season_id:
                        last_5_matches.append(match_data)
                    else:
                        break

        images.create_matches_statistics_image(
            riot_id,
            stats["rank"],
            stats["level"],
            stats["season_display_name"],
            last_5_matches,
            f"{api_puuid}"
        )

        view = views.StatsView(interaction, matches_list, api_puuid)
        await interaction.edit_original_message(content=None, embed=None, view=view, file=nextcord.File(
            f"statistics_images/overview/{api_puuid}.png"))

    @nextcord.slash_command(name="agent", description="View information about a VALORANT agent")
    @log_command
    async def agent(self, interaction: nextcord.Interaction, agent_name: str = SlashOption(name="agent", description="The agent you want to view", required=True, choices=characters)):
        await interaction.response.defer(with_message=True)
        agent_uuid = valorantInfo_db.get_info("character_name_to_id")['data'].get(agent_name)
        agent_stats = await valorantAPI.get_agent_stats(agent_uuid)
        if agent_stats.get("status") != 200:
            embed=nextcord.Embed(title="Error", description=f"{agent_stats.get('status')} - {agent_stats.get('error')}", color=colors.primary)
            return await interaction.edit_original_message(embed=embed)
        agent_data = agent_stats["data"]
        embed = nextcord.Embed(title=f"Agent Information",description=agent_data["description"], color=int(agent_data["backgroundGradientColors"][0][:-2], 16))
        embed.set_author(name=f"{agent_data['displayName']} | {agent_data['role']['displayName']}" , icon_url=agent_data["displayIcon"])
        embed.add_field(name=f"{agent_data['abilities'][0]['displayName']} (Ability 1)", value=f"{agent_data['abilities'][0]['description']}", inline=False)
        embed.add_field(name=f"{agent_data['abilities'][1]['displayName']} (Ability 2)", value=f"{agent_data['abilities'][1]['description']}", inline=False)
        embed.add_field(name=f"{agent_data['abilities'][2]['displayName']} (Ability 3)", value=f"{agent_data['abilities'][2]['description']}", inline=False)
        embed.add_field(name=f"{agent_data['abilities'][3]['displayName']} (Ultimate)", value=f"{agent_data['abilities'][3]['description']}", inline=False)
        embed.set_thumbnail(url=agent_data["fullPortrait"])

        return await interaction.edit_original_message(embed=embed)

    @nextcord.slash_command(name="weapon", description="View information about a VALORANT weapon")
    @log_command
    async def weapon(self, interaction: nextcord.Interaction, weapon_name: str = SlashOption(name="weapon", description="The weapon you want to view", required=True, choices=weapons)):
        await interaction.response.defer(with_message=True)
        weapon_uuid = valorantInfo_db.get_info("weapon_name_to_id")['data'].get(weapon_name)
        weapon_stats = await valorantAPI.get_weapon_stats(weapon_uuid)
        if weapon_stats.get("status") != 200:
            embed=nextcord.Embed(title="Error", description=f"{weapon_stats.get('status')} - {weapon_stats.get('error')}", color=colors.primary)
            return await interaction.edit_original_message(embed=embed)
        weapon_data = weapon_stats["data"]
        if weapon_data['weaponStats']["adsStats"] is None:
            zoom = "None"
        else:
            zoom = f"{weapon_data['weaponStats']['adsStats']['zoomMultiplier']}x"
        embed = nextcord.Embed(title=f"{weapon_data['displayName']} | Statistics", color=colors.primary)
        embed.add_field(name="Category", value=f"{weapon_data['category'].split('::')[1]}", inline=True)
        embed.add_field(name="Price", value=f"{weapon_data['shopData']['cost']}", inline=True)
        embed.add_field(name="Penetration", value=f"{weapon_data['weaponStats']['wallPenetration'].split('::')[1]}", inline=True)
        embed.add_field(name="Fire Rate", value=f"{weapon_data['weaponStats']['fireRate']}", inline=True)
        embed.add_field(name="Magazine Size", value=f"{weapon_data['weaponStats']['magazineSize']}", inline=True)
        embed.add_field(name="First Shot Accuracy", value=f"{weapon_data['weaponStats']['firstBulletAccuracy']}", inline=True)
        embed.add_field(name="Reload Time", value=f"{weapon_data['weaponStats']['reloadTimeSeconds']}s", inline=True)
        embed.add_field(name="Equip Time", value=f"{weapon_data['weaponStats']['equipTimeSeconds']}s", inline=True)
        embed.add_field(name="Zoom", value=f"{zoom}", inline=True)
        embed.set_image(url=weapon_data["displayIcon"])
        return await interaction.edit_original_message(embed=embed)

    @nextcord.slash_command(name="map", description="View information about a VALORANT map")
    @log_command
    async def map(self, interaction: nextcord.Interaction, map_name: str = SlashOption(name="map", description="The map you want to view", required=True, choices=maps)):
        await interaction.response.defer(with_message=True)
        map_uuid = valorantInfo_db.get_info("map_name_to_id")['data'].get(map_name)
        map_stats = await valorantAPI.get_map_stats(map_uuid)
        if map_stats.get("status") != 200:
            embed=nextcord.Embed(title="Error", description=f"{map_stats.get('status')} - {map_stats.get('error')}", color=colors.primary)
            return await interaction.edit_original_message(embed=embed)
        map_data = map_stats["data"]
        coordinates = map_data["coordinates"]
        splash = map_data["splash"]
        embed = nextcord.Embed(title=f"{map_data['displayName']} | Information", description=coordinates, color=colors.primary)
        embed.set_image(url=map_data["displayIcon"])
        embed.set_thumbnail(url=splash)
        return await interaction.edit_original_message(embed=embed)
    
    @nextcord.slash_command(name="skin", description="View information about a VALORANT weapon skin")
    @log_command
    async def skin(self, interaction: nextcord.Interaction, skin_name: str = SlashOption(name="skin", description="The skin you want to view", required=True)):
        skin_data = skin_id_to_data.get(skin_name_to_id.get(skin_name))
        if skin_data is None:
            embed = nextcord.Embed(description=f"Skin `{skin_name}` not found.", color=colors.primary)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        embed = nextcord.Embed(title=skin_data["displayName"], color=colors.primary)
        embed.set_image(url=skin_data["displayIcon"])
        view = views.SkinView(interaction, skin_data)
        return await interaction.response.send_message(embed=embed, view=view)
        
    @skin.on_autocomplete("skin_name")
    async def autocomplete_skin(self, ctx, skin_name: str):
        if skin_name == "":
            # return the first 10 skins
            return skin_names[:10]
        skins = []
        for name in skin_names:
            ratio = Levenshtein.ratio(name.lower(), skin_name.lower())
            skins.append((name, ratio))

        skins = sorted(skins, key=lambda x: x[1], reverse=True)
        return [skin[0] for skin in skins[:10]]
    
    @nextcord.slash_command(name="patch-notes", description="Get the latest patch notes")
    @log_command
    async def patch_notes(self, interaction: nextcord.Interaction):
        """ patch_notes_data = await patchAndNews.get_latest_patch_notes()
        date_object = datetime.fromisoformat(patch_notes_data["date"].replace('Z', '+00:00'))
        embed = nextcord.Embed(
            title=patch_notes_data["title"],
            description=patch_notes_data["description"],
            url=f"https://playvalorant.com/en-us{patch_notes_data['url']['url']}",
            timestamp=date_object,
            color=colors.primary)
        embed.set_image(url=patch_notes_data["banner"]["url"])
        embed.set_author(name="Riot Games | PlayVALORANT", url="https://playvalorant.com/en-us/news/")
        view = views.PatchAndNewsView(f"https://playvalorant.com/en-us{patch_notes_data['url']['url']}", patch_notes_data["title"])
        return await interaction.response.send_message(embed=embed, view=view) """
        embed = nextcord.Embed(title="Command Temporarily Unavailable", description="Due to recent updates in the Riot Games API, this command is currently not working. We are aware of the issue and are working on updating our bot to be compatible with the latest changes. Thank you for your patience! 🛠️\n\nIf you still wish to view the Patch Notes visit https://playvalorant.com/en-us/news/game-updates/", color=colors.primary)
        return await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="news", description="Get the latest news")
    @log_command
    async def news(self, interaction: nextcord.Interaction):
        """ news_data = await patchAndNews.get_latest_news()
        date_object = datetime.fromisoformat(news_data["date"].replace('Z', '+00:00'))
        url = None
        if news_data["article_type"] == "Normal article":
            url = f"https://playvalorant.com/en-us{news_data['url']['url']}"
        else:
            url = news_data["external_link"]
        embed = nextcord.Embed(
            title=news_data["title"],
            description=news_data["description"],
            url=url,
            timestamp=date_object,
            color=colors.primary)
        embed.set_image(url=news_data["banner"]["url"])
        embed.set_author(name="Riot Games | PlayVALORANT", url="https://playvalorant.com/en-us/news/")
        view = views.PatchAndNewsView(url, news_data["title"])
        return await interaction.response.send_message(embed=embed, view=view) """
        embed = nextcord.Embed(title="Command Temporarily Unavailable", description="Due to recent updates in the Riot Games API, this command is currently not working. We are aware of the issue and are working on updating our bot to be compatible with the latest changes. Thank you for your patience! 🛠️\n\nIf you still wish to view the News visit https://playvalorant.com/en-us/news/", color=colors.primary)
        return await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(StatisticsCog(bot))