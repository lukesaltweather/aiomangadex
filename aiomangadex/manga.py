import asyncio
import difflib
import io
import json

import aiohttp

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import List, Union, Dict

from .chapter import Chapter
from .chapterlist import ChapterList
from .base import MangadexBase


@dataclass(frozen=True)
class Manga(MangadexBase):

    title: str = None
    altTitles: List[str] = None
    description: str = None
    artist: List[str] = None
    author: List[str] = None
    publication: Dict = None
    tags: List[int] = None
    lastChapter: int = None
    lastVolume: int = None
    isHentai: bool = None
    links: Dict = None
    relations: List[str] = None
    rating: Dict = None
    views: int = None
    follows: int = None
    comments: int = None
    lastUploaded: datetime = None
    mainCover: str = None
    chapters: ChapterList = None

    @classmethod
    def from_json(cls, json, http):
        manga_data = json.pop('manga')
        lastUploaded = datetime.fromtimestamp(manga_data.pop('lastUploaded', 0))
        chapters = ChapterList.from_partial_chapters(json.pop('chapters', []))
        return cls(lastUploaded=lastUploaded, chapters=chapters, http=http, **manga_data)

    async def fetch_chapter(self, *, language=None, number=None, volume=None, multiple=False) -> Union[Chapter, ChapterList]:
        raise NotImplementedError

    def upload_chapter(self, filestream, chapter: str, lang_id: str, group_id: int, *, title=None, volume=None, group_id_2=None, group_id_3=None):
        return self.http.upload_chapter(filestream, manga_id=self.id, lang_id=lang_id, volume=volume, chapter_number=chapter, chapter_title=title, group_id=group_id, group_id_2=group_id_2, group_id_3=group_id_3)
