import aiohttp

async def get_patch_notes():
	async with aiohttp.ClientSession() as session:
		async with session.get("https://playvalorant.com/page-data/en-us/news/tags/patch-notes/page-data.json") as response:
			data = await response.json()
			return data
		
async def get_latest_patch_notes():
	data = await get_patch_notes()
	return data["result"]["data"]["articles"]["nodes"][0]

async def get_news():
	async with aiohttp.ClientSession() as session:
		async with session.get("https://playvalorant.com/page-data/en-us/news/page-data.json") as response:
			data = await response.json()
			return data
		
async def get_latest_news():
	data = await get_news()
	return data["result"]["data"]["allContentstackArticles"]["nodes"][0]