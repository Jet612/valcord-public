import valaw
from . import database, variables

valawClient = valaw.Client(variables.RIOT_API_KEY, cluster="americas")
riot_api_db = database.RiotAPICollection()

async def get_match(match_id, region):
    match_data = riot_api_db.get_match(match_id)
    if match_data:
        return match_data
    match_data = await valawClient.GET_getMatch(match_id, region)
    riot_api_db.add_match(match_data)
    return match_data