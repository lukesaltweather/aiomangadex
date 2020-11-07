import asyncio

from .session import MangadexSession
from .manga import Manga

class MangadexClient:

    __slots__ = ('http', '_user_cache', '_manga_cache', '_chapter_cache', '_group_cache', '__dict__')

    def __init__(self, cache):
        self.http = MangadexSession()
        # generate session here, setup login here

    #base methods to fetch things
    #implement cache here
    async def fetch_manga(self, manga_id: int, include_chapters=False):
        res = await self.http.get_manga(manga_id, include_partial_chapters=include_chapters)
        return Manga()