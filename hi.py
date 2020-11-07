from aiomangadex import session, partialchapter
import asyncio
import aiohttp

async def create_session():
    session = aiohttp.ClientSession()
    cl = session.MangadexClient(session, asyncio.get_event_loop())
    await cl.wait_until_ready()
    chps = await cl.get_manga(34198, include_partial_chapters=True)
    print(chps)
    for ch in chps['chapters']:
        print(partialchapter.PartialChapter.from_json(ch))
    await session.close()

asyncio.get_event_loop().run_until_complete(create_session())