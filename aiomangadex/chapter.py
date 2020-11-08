import json

import aiohttp
import difflib
import io
import asyncio

from aiomangadex.language import Language
from aiomangadex.partialchapter import PartialChapter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import List, Union

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

@dataclass(frozen=True)
class Chapter(PartialChapter):
    """Representation of the chapter model

    Attributes:
        id (int): ID of the chapter
        manga_id (int): ID of the chapter's manga
        volume (int): Which volume the chapter is in
        hash (str): Chapter hash used in the img links
        chapter (float): Chapter Number
        title (str): Chapter Title
        lang_code (str): Language of the translation
        lang_name (str): Language of the translation
        group_id (int): Scanlation Group 1
        group_name (str): Scanlation Group 1
        group_id_2 (int): Scanlation Group
        group_name_2 (str): Scanlation Group
        group_id_3 (int): Scanlation Group
        group_name_3 (str): Scanlation Group
        timestamp (int): 
        comments (int): Amount of comments
        server (str): Server chapter is hosted on, used for the img urls
        page_array (List[str]): Array with links to the pages
        long_strip (bool): Whether Chapter is in strip format
        status (str): Status
        links (List[str]): | Links to the pages.
            | *This is not provided by the api, but put together by the library.*
        session (aiohttp.ClientSession): The session passed initially, or the one created by the library if *None* was passed.
    Warnings:
        If this wasn't fetched through :meth:`fetch_chapter` it is missing some information coming from another API endpoint, like the links to the pages.
        This is fetched automatically if you use :meth:`download_pages() <Chapter.download_page>` or :meth:`download_all_pages() <Chapter.download_all_pages>`.
        To just fetch the missing data, use :meth:`fetch_pages()`
    """
    group_id: int = None
    group_nae: str = None
    group_id_2: int = None
    group_name_2: str = None
    group_id_3: int = None
    group_name_3: str = None
    server: str = None
    page_array: List[str] = None
    long_strip: bool = None
    status: str = None
    links: List[str] = None

    async def download_page(self, page: int, data_saver: bool=True):
        """

        Args:
            page (int): Index of page to download
            data_saver (bool, optional): Whether to use the mangadex datasaver mode for images. Defaults to True.

        Returns:
            io.BytesIO: A buffer with the image.
        """
        if self.links is None:
            await self.fetch_pages(data_saver)
        link = self.links[page]
        async with self.session.get(link) as resp:
            return io.BytesIO(await resp.read())

    def download_all_pages(self, data_saver: bool=True):
        """
        Return a (async) generator to download all pages.

        Warnings:
            Fast because it runs all download simultaneously. Keep this in mind if you use it often, as you might get banned.

        Args:
            data_saver (bool): Whether to use the data-saver option or not.

        Returns:
            AsyncGenerator [ io.BytesIO ]: Generator with downloaded pages.
        """
        async def generator():
            if self.links is None:
                await self.fetch_pages(data_saver)
            futures = [_download_file(self.session, url) for url in self.links]
            for future in futures:
                yield await future
        return generator()
        #   return await asyncio.gather(*download_futures)

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