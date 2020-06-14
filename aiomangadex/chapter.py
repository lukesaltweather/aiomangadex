import aiohttp
import difflib
import io
import asyncio

from aiomangadex.language import Language
from dataclasses import dataclass
from typing import List, Union

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

@dataclass
class Chapter:
    """ A class that matches the chapter endpoint.
    """
    id: int = None
    manga_id: int = None
    volume: int = None
    hash: str = None
    chapter: float = None
    title: str = None
    lang_code: str = None
    lang_name: str = None
    group_id: int = None
    group_name: str = None
    group_id_2: int = None
    group_name_2: str = None
    group_id_3: int = None
    group_name_3: str = None
    timestamp: int = None
    comments: int = None
    server: str = None
    page_array: List[str] = None
    long_strip: bool = None
    status: str = None
    links: List[str] = None
    session: aiohttp.ClientSession = None
    _user_session: bool = False

    async def download_page(self, page: int, data_saver: bool=True) -> io.BytesIO:
        """

        Args:
            page (int): Index of page to download
            data_saver (bool, optional): Whether to use the mangadex datasaver mode for images. Defaults to True.

        Returns:
            io.BytesIO: A buffer with the image.
        """
        if self.links is None:
            link = (await self.fetch_pages(data_saver))[page]
        else:
            link = self.links[page]
        async with self.session.get(link) as resp:
            return io.BytesIO(await resp.read())

    async def download_all_pages(self, data_saver: bool=True) -> List[io.BytesIO]:
        if self.links is None:
            links = (await self.fetch_pages(data_saver))
        else:
            links = self.links
        download_futures = [download_file(self.session, url) for url in links]
        return await asyncio.gather(*download_futures)

    async def fetch_pages(self, data_saver: bool=True) -> List[str]:
        d = "data-saver" if data_saver else "data"
        if self.page_array is None:
            await self._fetch()
        self.links = []
        server = self.server.replace('data/', '')
        for link in self.page_array:
            self.links.append(f'{server}{d}/{self.hash}/{link}')
        return self.links

    async def _fetch(self):
        async with self.session.get(f'https://mangadex.org/api/chapter/{self.id}') as r:
            resp = await r.json()
        for key, value in resp.items():
            setattr(self, key, value)


    def __del__(self):
        if not self._user_session:
            asyncio.create_task(self.session.close())

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
