import asyncio
from dataclasses import dataclass
import aiohttp
import ujson
from typing import List, Union
import io
import difflib

async def download_file(session: aiohttp.ClientSession, url: str) -> io.BytesIO:
    """Helper function for downloading.

    Args:
        session (aiohttp.ClientSession): active Session
        url (str): URL to image

    Returns:
        io.BytesIO: Buffer with Image
    """
    async with session.get(url) as response:
        assert response.status == 200
        # For large files use response.content.read(chunk_size) instead.
        return io.BytesIO(await response.read())
        

class Language:
    """ A class with a bunch of class methods to aid with finding a chapter in the desired language.
    """
    def __init__(self, code, scdry):
        self._lang_code = code
        self._scdry = scdry

    def __eq__(self, other):
        if other in [self._lang_code, self._scdry]:
            return True
        return False

    @classmethod
    def English(cls):
        return cls('gb')

    @classmethod
    def German(cls):
        return cls('de')

    @classmethod
    def French(cls):
        return cls('fr')

    @classmethod
    def Dutch(cls):
        return cls('nl')
    
    @classmethod
    def Spanish(cls):
        return cls('es', 'mx')

    @classmethod
    def Mexican(cls):
        return cls('es', 'mx')

@dataclass
class Chapter:
    """ A class that matches the chapter endpoint.
    """
    id: int = None
    volume: int = None
    chapter: float = None
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
        """

        Args:
            page (int): Index of page to download
            data_saver (bool, optional): Whether to use the mangadex datasaver mode for images. Defaults to True.

        Returns:
            io.BytesIO: A buffer with the image.
        """
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

class ChapterList:
    """ A class used for managing and filtering a Manga Instance's chapters.
    """
    def __init__(self, chapters: List[Chapter]):
        self._chapters = chapters

    def __getitem__(self, i):
        return self._chapters[i]

    def _append(self, element: Chapter):
        self._chapters.append(element)
        return self._chapters

    def filter_language(self, *lang: Union[Language, str]) -> 'ChapterList':
        """Filter by languages, connected by logical OR.
        Returns a ChapterList of the chapters with corresponding languages.

        Returns:
            ChapterList
        """
        if not isinstance(lang, Language):
            lang = Language(lang)
        chapters = []
        for chapter in self._chapters:
            if chapter.lang_code in lang:
                chapters.append(chapter)
        return ChapterList(chapters)
        
    def filter_title(self, *titles, difference_cutoff: float = 0.8) -> 'ChapterList':
        """Filter by titles, connected by logical OR.
        Returns a ChapterList of the chapters with corresponding titles.

        Returns:
            ChapterList
        """
        chapters = list()
        tit = [chapter.title for chapter in self._chapters]
        results = list()
        for t in titles:
            results.append(difflib.get_close_matches(t, tit, cutoff=difference_cutoff))

        for chapter in self._chapters:
            if chapter.title in results:
                chapters.append(chapter)
        
        return ChapterList(chapters)

    def filter_chapter_number(self, *numbers: List[int]) -> 'ChapterList':
        """Filter by chapter number, connected by logical OR.
        Returns a ChapterList of the chapters with according chapter numbers.

        Returns:
            ChapterList
        """
        li = []
        for chapter in self._chapters:
            if float(chapter.chapter) in numbers:
                li.append(chapter)
        return ChapterList(li)

    def filter_id(self, *ids: List[int]) -> 'ChapterList':
        """
        Filter by id, connected by logical OR.
        Returns ChapterList of chapters with corresponding ids.

        Returns:
            ChapterList
        """
        li = []
        for chapter in self._chapters:
            if float(chapter.id) in ids:
                li.append(chapter)
        return ChapterList(li)

    def __len__(self):
        return len(self._chapters)

@dataclass(frozen=True)
class Manga:
    id: int
    cover_url : str
    description : str
    rating: dict
    alt_names: list
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
    chapters: ChapterList
    session: aiohttp.ClientSession = None
    _user_session : bool = False

    async def close_session(self):
        await self.session.close()

    def __del__(self):
        if not self._user_session:
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
    chapters.reverse()
    return Manga(**dict(response.get('manga')), chapters=ChapterList(chapters), id=manga_id, session=session, _user_session=user_session)

async def fetch_chapter(chapter_id: int, session: aiohttp.ClientSession = None) -> Chapter:
    if session is not None:
        user_session = True
        session._json_serialize=ujson.dumps
        async with session.get(f'https://mangadex.org/api/chapter/{chapter_id}') as resp:
            response = await resp.json()
    else:
        user_session = False
        session = aiohttp.ClientSession(json_serialize=ujson.dumps)
        async with session.get(f'https://mangadex.org/api/chapter/{chapter_id}') as resp:
            response = await resp.json()
    return Chapter()