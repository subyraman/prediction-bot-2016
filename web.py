import aiohttp

async def get_page(url):
    res = await aiohttp.get(url)
    text = await res.text()
    return text
