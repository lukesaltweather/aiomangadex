import asyncio
from dataclasses import dataclass
import aiohttp
import ujson
from typing import List, Union
import io

async def download_file(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        assert response.status == 200
        # For large files use response.content.read(chunk_size) instead.
        return io.BytesIO(await response.read())

class Language:
    def __init__(self, code):
        self.lang_code = code

    def __eq__(self, other):
        if self.lang_code == other:
            return True
        return False

    @classmethod
    def English(cls):
        return cls('gb')

    @classmethod
    def German(cls):
        return cls('de')

@dataclass
class Chapter:
    id: int = None
    volume: int = None
    chapter: int = None
    title: str = None
    lang_code: str = None
    group_id: int = None
    group_name: str = None
    group_id_2: int = None
    group_name_2: str = None
    group_id_3: int = None
    group_name_3: str = None
    timestamp: int = None
    links : List[str] = None
    session: aiohttp.ClientSession = None

    async def download_page(self, page: int, data_saver: bool=True) -> io.BytesIO:
        if self.links is None:
            link = (await self.fetch_page_links(data_saver))[page]
        else:
            link = self.links[page]
        async with self.session.get(link) as resp:
            return io.BytesIO(await resp.read())

    async def download_all_pages(self, data_saver: bool=True) -> List[io.BytesIO]:
        if self.links is None:
            links = (await self.fetch_page_links(data_saver))
        else:
            links = self.links
        download_futures = [download_file(self.session, url) for url in links]
        return await asyncio.gather(*download_futures)

    async def fetch_page_links(self, data_saver: bool=True) -> List[str]:
        d = "data-saver" if data_saver else "data"
        async with self.session.get(f'https://mangadex.org/api/chapter/{self.id}') as r:
            resp = await r.json()
        self.links = []
        for link in resp.get('page_array'):
            self.links.append(f'https://mangadex.org/{d}/{resp.get("hash")}/{link}')
        return self.links

@dataclass(frozen=True)
class Manga:
    id: int
    cover_url : str
    description : str
    title : str
    artist: str
    author: str
    status: int
    genres: list
    last_chapter: int
    lang_name: str
    lang_flag: str
    hentai: bool
    links: dict
    chapters: List[Chapter]
    session: aiohttp.ClientSession = None
    user_session : bool = False

    def find_chapters(self, title: str = None, id: int = None, language: Union[Language, str] = None, chapter_number: int = None) -> List[Chapter]:
        pass

    async def close_session(self):
        await self.session.close()

    def __del__(self):
        if not self.user_session:
            asyncio.create_task(self.session.close())

async def fetch_manga(manga_id: int, session: aiohttp.ClientSession = None) -> Manga:
    if session is not None:
        user_session = True
        session._json_serialize=ujson.dumps
        async with session.get(f'https://mangadex.org/api/manga/{manga_id}') as resp:
            response = await resp.json()
    else:
        user_session = False
        session = aiohttp.ClientSession(json_serialize=ujson.dumps)
        async with session.get(f'https://mangadex.org/api/manga/{manga_id}') as resp:
            response = await resp.json()
    chapters = []
    for key, value in response.get('chapter').items():
        chapters.append(Chapter(id=key, **dict(value), session=session))
    return Manga(**dict(response.get('manga')), chapters=chapters, id=manga_id, session=session, user_session=user_session)