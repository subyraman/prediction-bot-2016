async def get_page(client, url):
    async with client.get(url) as res:
        text = await res.text()
        return text
