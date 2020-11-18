import asyncio
import io

from collections import AsyncIterator
from typing import Any, Awaitable
from inspect import isawaitable

import aiohttp

async def _download_file(session: aiohttp.ClientSession, url: str) -> io.BytesIO:
    """Helper function for downloading.

    Args:
        session (aiohttp.ClientSession): active Session
        url (str): URL to image

    Returns:
        io.BytesIO: Buffer with Image
    """
    async with session.get(url) as response:
        assert response.status == 200
        return io.BytesIO(await response.read())

def always_await(o: Any) -> Awaitable:
    if isawaitable(o):
        return o
    fut = asyncio.get_event_loop().create_future()
    fut.set_result(o)
    return fut

def zip_folder():
    pass

class ChapterIterator:
    def __init__(self, session, base_url, *, limit = 50):
        self.limit = limit
        self.current_page = 1
        self.session = session
        self.base_url = session
        super().__init__()

    async def next(self):
        return self.session._request(Route())

    def __anext__(self):
        return self.next()

    async def flatten(self):
        ret = []
        while True:
            try:
                i = await self.next()
            except StopAsyncIteration as e:
                return ret
            else:
                ret.append(i)