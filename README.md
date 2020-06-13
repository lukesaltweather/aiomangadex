# aiomangadex

An asynchronous API wrapper for mangadex.

  

# Basic Usage

       from aiomangadex import aiomangadex
       import asyncio
       async def get_manga(id):
	       manga = await aiomangadex.fetch_manga(id)
	       print(manga.title)
       asyncio.run(get_manga(1))
### For more info, visit the docs [here.](https://aiomangadex.readthedocs.io)