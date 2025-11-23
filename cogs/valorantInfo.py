import nextcord
from nextcord.ext import commands, tasks
from utils import variables, database
import valaw
import asyncio
import aiohttp

client = valaw.Client(variables.RIOT_API_KEY, cluster="americas")
valorantInfo_db = database.ValorantInfo()

async def fetch_skins_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://valorant-api.com/v1/weapons/skins") as response:
            skins_data = await response.json()
            return skins_data

class valorantInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.get_content.start()
        self.update_season.start()

    @tasks.loop(hours=6)
    async def get_content(self):
        content_data = await client.GET_getContent("na", locale="en-US")
        skins_data = await fetch_skins_data()

        valorantInfo_db.create_new_info("skin_names", [x["displayName"] for x in skins_data["data"]])
        valorantInfo_db.create_new_info("skin_name_to_id", {x["displayName"]: x["uuid"] for x in skins_data["data"]})
        valorantInfo_db.create_new_info("skin_id_to_name", {x["uuid"]: x["displayName"] for x in skins_data["data"]})
        valorantInfo_db.create_new_info("skin_id_to_data", {x["uuid"]: x for x in skins_data["data"]})

        valorantInfo_db.create_new_info("character_name_to_id", {x.name: x.id for x in content_data.characters})
        valorantInfo_db.create_new_info("character_id_to_name", {x.id: x.name for x in content_data.characters})
        valorantInfo_db.create_new_info("characters", [x.name for x in content_data.characters if x.id != "DED3520F-4264-BFED-162D-B080E2ABCCF9"])

        valorantInfo_db.create_new_info("map_name_to_id", {x.name: x.id for x in content_data.maps})
        valorantInfo_db.create_new_info("map_id_to_name", {x.id: x.name for x in content_data.maps})
        valorantInfo_db.create_new_info("map_path_to_name", {x.assetPath: x.name for x in content_data.maps[1:]})
        valorantInfo_db.create_new_info("maps", [x.name for x in content_data.maps if x.id != "7A929CD8-4021-C128-5A21-BC896C1929BA"])

        valorantInfo_db.create_new_info("mode_name_to_id", {x.name: x.id for x in content_data.gameModes})
        valorantInfo_db.create_new_info("mode_id_to_name", {x.id: x.name for x in content_data.gameModes})

        valorantInfo_db.create_new_info("weapon_name_to_id", {x.name: x.id for x in content_data.equips})
        valorantInfo_db.create_new_info("weapon_id_to_name", {x.id: x.name for x in content_data.equips})
        valorantInfo_db.create_new_info("weapons", [x.name for x in content_data.equips if x.id not in ["2F59173C-4BED-B6C3-2191-DEA9B58BE9C7", "0AFB2636-4093-C63B-4EF1-1E97966E2A3E", "9677D521-45F0-0EFF-AD21-81A03FC8A314", "95336AE4-45D4-1032-CFAF-6BAD01910607", "3DE32920-4A8F-0499-7740-648A5BF95470", "6BD46791-4F27-AA65-7D67-3F8D9D8B8B90", "2E20A5AF-4726-95F6-7D9C-9DB9A18DADA9", "D002A9A2-4B43-86C6-1DBC-58BC7815FF9C", "9438BE81-46B8-D8B0-8A66-F9A0251FB728", "193C78AF-4498-4D51-C445-ADAC288425BE", "129B0CFB-4C77-45E5-BA86-5694B231B242", "2A117B48-4BED-0701-5DCD-FCAC06047735", "5261A41B-4C56-8EB5-9E46-7193F363477E", "856D9A7E-4B06-DC37-15DC-9D809C37CB90", "39099FB5-4293-DEF4-1E09-2E9080CE7456"]])

        """ broad_rank_dictionary = {"0": "Unranked",
                            "3": "Iron",
                            "4": "Iron",
                            "5": "Iron",
                            "6": "Bronze",
                            "7": "Bronze",
                            "8": "Bronze",
                            "9": "Silver",
                            "10": "Silver",
                            "11": "Silver",
                            "12": "Gold",
                            "13": "Gold",
                            "14": "Gold",
                            "15": "Platinum",
                            "16": "Platinum",
                            "17": "Platinum",
                            "18": "Diamond",
                            "19": "Diamond",
                            "20": "Diamond",
                            "21": "Ascendant",
                            "22": "Ascendant",
                            "23": "Ascendant",
                            "24": "Immorant",
                            "25": "Immorant",
                            "26": "Immorant",
                            "27": "Radiant"}
        valorantInfo_db.create_new_info("broad_rank_dictionary", broad_rank_dictionary) """

        rank_dictionary_by_ids = {"0": "Unranked",
                            "3": "Iron 1",
                            "4": "Iron 2",
                            "5": "Iron 3",
                            "6": "Bronze 1",
                            "7": "Bronze 2",
                            "8": "Bronze 3",
                            "9": "Silver 1",
                            "10": "Silver 2",
                            "11": "Silver 3",
                            "12": "Gold 1",
                            "13": "Gold 2",
                            "14": "Gold 3",
                            "15": "Platinum 1",
                            "16": "Platinum 2",
                            "17": "Platinum 3",
                            "18": "Diamond 1",
                            "19": "Diamond 2",
                            "20": "Diamond 3",
                            "21": "Ascendant 1",
                            "22": "Ascendant 2",
                            "23": "Ascendant 3",
                            "24": "Immortal 1",
                            "25": "Immortal 2",
                            "26": "Immortal 3",
                            "27": "Radiant"}
        valorantInfo_db.create_new_info("rank_dictionary_by_ids", rank_dictionary_by_ids)
        valorantInfo_db.create_new_info("rank_dictionary_by_names", {v: k for k, v in rank_dictionary_by_ids.items()})

        rank_emoji_dictionary = {"Unranked": "<:Unranked:1068423200574279701>",
                            "Iron 1": "<:Iron_1:1026893491961335858>",
                            "Iron 2": "<:Iron_2:1026893492678557737>",
                            "Iron 3": "<:Iron_3:1026893494473719838>",
                            "Bronze 1": "<:Bronze_1:1026893472524927026>",
                            "Bronze 2": "<:Bronze_2:1026893473825165333>",
                            "Bronze 3": "<:Bronze_3:1026893476056547417>",
                            "Silver 1": "<:Silver_1:1026893507182477415>",
                            "Silver 2": "<:Silver_2:1026893508289757224>",
                            "Silver 3": "<:Silver_3:1026893509216710707>",
                            "Gold 1": "<:Gold_1:1026893481945346110>",
                            "Gold 2": "<:Gold_2:1026893483635646544>",
                            "Gold 3": "<:Gold_3:1026893485560840192>",
                            "Platinum 1": "<:Platinum_1:1026893495555858543>",
                            "Platinum 2": "<:Platinum_2:1026893496948371637>",
                            "Platinum 3": "<:Platinum_3:1026893504372285491>",
                            "Diamond 1": "<:Diamond_1:1026893477725872198>",
                            "Diamond 2": "<:Diamond_2:1026893479290351686>",
                            "Diamond 3": "<:Diamond_3:1026893480804491334>",
                            "Ascendant 1": "<:Ascendant_1:1026893454577520640>",
                            "Ascendant 2": "<:Ascendant_2:1026893457106669568>",
                            "Ascendant 3": "<:Ascendant_3:1026893470868193340>",
                            "Immortal 1": "<:Immortal_1:1026893486978510888>",
                            "Immortal 2": "<:Immortal_2:1026893488912072914>",
                            "Immortal 3": "<:Immortal_3:1026893490711441448>",
                            "Radiant": "<:Radiant:1026893506083561472>"}
        valorantInfo_db.create_new_info("rank_emoji_dictionary", rank_emoji_dictionary)

        agent_emoji_dictionary = {"Yoru": "<:Yorudisplay:1051411978532425779>",
                                "Viper": "<:Viperdisplay:1051412002012135434>",
                                "Sova": "<:Sovadisplay:1051412029476458588>",
                                "Skye": "<:Skyedisplay:1051412051811110972>",
                                "Sage": "<:Sagedisplay:1051412077861928980>",
                                "Reyna": "<:Reynadisplay:1051412101211635742>",
                                "Raze": "<:Razedisplay:1051412129489625138>",
                                "Phoenix": "<:Phoenixdisplay:1051412151551660072>",
                                "Omen": "<:Omendisplay:1051412171109707808>",
                                "Neon": "<:Neondisplay:1051412193113018388>",
                                "Killjoy": "<:Killjoydisplay:1051412213304393728>",
                                "KAY/O": "<:KAYOdisplay:1051412233026031627>",
                                "Jett": "<:Jettdisplay:1051412250243649536>",
                                "Breach": "<:Breachdisplay:1051412392262783096>",
                                "Brimstone": "<:Brimstonedisplay:1051412367201808384>",
                                "Cypher": "<:Cypherdisplay:1051412339364200458>",
                                "Chamber": "<:Chamberdisplay:1051412314802376724>",
                                "Astra": "<:Astradisplay:1051412418821107752>"}
        valorantInfo_db.create_new_info("agent_emoji_dictionary", agent_emoji_dictionary)
        
        gamemode_emojis_by_asset_path = {"/Game/GameModes/Bomb/BombGameMode.BombGameMode_C": "<:Standard:1065346771221499955>",
                        "/Game/GameModes/Deathmatch/DeathmatchGameMode.DeathmatchGameMode_C": "<:Deathmatch:1065346763139076146>",
                        "/Game/GameModes/Escalation/EscalationGameMode_PrimaryAsset_C": "<:Escalation:1065346765051666502>",
                        "/Game/GameModes/NewPlayerExperience/NPEGameMode.NPEGameMode_C": "<:Onboarding:1065346766326739024>",
                        "/Game/GameModes/OneForAll/OneForAll_GameMode.OneForAll_GameMode_C": "<:Replication:1065346768021245992>",
                        "/Game/GameModes/QuickBomb/QuickBombGameMode.QuickBombGameMode_C": "<:SpikeRush:1065346770114203698>",
                        "/Game/GameModes/ShootingRange/ShootingRangeGameMode.ShootingRangeGameMode_C": "<:PRACTICE:1065346772349763745>",
                        "/Game/GameModes/SnowballFight/SnowballFightGameMode.SnowballFightGameMode_C": "<:SnowballFight:1065346771221499955>",
                        "/Game/GameModes/_Development/Swiftplay_EndOfRoundCredits/Swiftplay_EoRCredits_GameMode.Swiftplay_EoRCredits_GameMode_C": "<:Swiftplay:1065346772349763745>"}
        valorantInfo_db.create_new_info("gamemode_emojis_by_asset_path", gamemode_emojis_by_asset_path)

    async def get_act_short_name(self, act_id: str) -> str:
        async with aiohttp.ClientSession() as session:
            url = f"https://valorant-api.com/v1/seasons/{act_id}"
            async with session.get(url) as resp:
                data = await resp.json()
            url2 = f"https://valorant-api.com/v1/seasons/{data['data']['parentUuid']}"
            async with session.get(url2) as resp:
                data2 = await resp.json()
            return f"E{data2['data']['displayName'].split(' ')[1]}:A{data['data']['displayName'].split(' ')[1]}"
        
    @tasks.loop(minutes=30)
    async def update_season(self):
        content_data = await client.GET_getContent("na", locale="en-US")
        current_act = None
        current_episode = None
        for act in content_data.acts:
            if act.isActive:
                if act.type == "act":
                    current_act = act
                elif act.type == "episode":
                    current_episode = act
        valorantInfo_db.create_new_info("current_season", {"act_id": current_act.id, "act_name": current_act.name, "act_parent_id": current_act.parentId, "episode_id": current_episode.id, "episode_name": current_episode.name, "episode_parent_id": current_episode.parentId})

class Exceptions:
    class StatusError(Exception):
        """A status was raised."""

def setup(bot):
    bot.add_cog(valorantInfoCog(bot))
