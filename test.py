from bs4 import BeautifulSoup
import datetime
import aiohttp
import asyncio

url = "https://mail.ru/"


async def test():

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            time = datetime.datetime.now()
            html = await response.text()
            print(datetime.datetime.now() - time)
            time = datetime.datetime.now()
            soup = BeautifulSoup(html, "lxml")
            print(datetime.datetime.now() - time)
            print(soup.find("meta"))


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
