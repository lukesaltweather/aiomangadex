from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .base import MangadexBase
from .exceptions import MangadexException
from .group import Group
from .language import Language

@dataclass(frozen=True)
class PartialChapter(MangadexBase):
    hash: str = None
    mangaId: int = None
    mangaTitle: int = None
    volume: float = None
    chapter: float = None
    title: str = None
    groups: List[int] = field(default_factory=list)
    uploader: int = None
    language: Language = Language.NoLang()
    timestamp: datetime = None
    comments: int = 0
    views: int = None

    def __hash__(self):
        return self.hash

    @classmethod
    def from_json(cls, json, http):
        timestamp = datetime.fromtimestamp(json.pop('timestamp'))
        language = Language(json.pop('language'))
        return cls(timestamp=timestamp, http=http, language=language, **json)

    async def download_page(self, page: int, data_saver: bool=True):
        raise NotImplementedError("Cannot download pages from PartialChapter. Fetch full chapter first.")

    def download_all_pages(self, data_saver: bool=True):
        raise NotImplementedError("Cannot download pages from PartialChapter. Fetch full chapter first.")

    async def fetch_full(self):
        from .chapter import Chapter
        return Chapter.from_json(await self.http.fetch_chapter(self.id), http=self.http)

    async def fetch_uploader(self):
        raise NotImplementedError