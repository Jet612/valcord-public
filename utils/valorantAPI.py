import aiohttp

async def get_agent_stats(agent_uuid):
    async with aiohttp.ClientSession() as session:
        url=f"https://valorant-api.com/v1/agents/{agent_uuid}"
        async with session.get(url) as resp:
            agent_data = await resp.json()
    return agent_data

async def get_weapon_stats(weapon_uuid):
    async with aiohttp.ClientSession() as session:
        url=f"https://valorant-api.com/v1/weapons/{weapon_uuid}"
        async with session.get(url) as resp:
            weapon_data = await resp.json()
    return weapon_data

async def get_map_stats(map_uuid):
    async with aiohttp.ClientSession() as session:
        url=f"https://valorant-api.com/v1/maps/{map_uuid}"
        async with session.get(url) as resp:
            map_data = await resp.json()
    return map_data