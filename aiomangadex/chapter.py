
import io

from .language import Language
from .partialchapter import PartialChapter
from .util import _download_file

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union

PartialGroup = namedtuple('PartialGroup', ('id', 'name'))

@dataclass(frozen=True)
class Chapter(PartialChapter):

    groups: List[PartialGroup] = None
    server: str = None
    page_array: List[str] = None
    long_strip: bool = None
    status: str = None
    pages: List[str] = None
    links: List[str] = None

    async def download_page(self, page: int, data_saver: bool=True):
        """

        Args:
            page (int): Index of page to download
            data_saver (bool, optional): Whether to use the mangadex datasaver mode for images. Defaults to True.

        Returns:
            io.BytesIO: A buffer with the image.
        """
        link = self.links[page]
        async with self.http._session.get(link) as resp:
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
            futures = [_download_file(self.http._session, url) for url in self.links]
            for future in futures:
                yield await future
        return generator()
        #   return await asyncio.gather(*download_futures)

    @classmethod
    def from_json(cls, json, http):
        timestamp = datetime.fromtimestamp(json.pop('timestamp'))
        server = json.get('server')
        hash = json.get('hash')
        links = [f'{server}{hash}/{img}' for img in json.get('pages')]
        groups = [PartialGroup(id, name) for id, name in json.pop('groups').values()]
        language = Language(json.pop('language'))
        return cls(timestamp=timestamp, http=http, links=links, groups=groups, language=language, **json)