import asyncio
import difflib
import io
import json

import aiohttp

from dataclasses import dataclass
from typing import List, Union

from .chapter import Chapter, ChapterList
from .base import MangadexBase


@dataclass(frozen=True)
class Manga(MangadexBase):

    id: int = None
    cover_url: str = None
    description: str = None
    rating: dict = None
    demographic: int = None
    last_volume: int = None
    last_updated: int = None
    alt_names: list = None
    title : str = None
    artist: str = None
    author: str = None
    status: int = None
    genres: list = None
    last_chapter: int = None
    lang_name: str = None
    lang_flag: str = None
    hentai: bool = None
    links: dict = None
    related: List = None
    views: int = None
    follows: int = None
    covers: List[str] = None
    comments: int = None
    chapters: ChapterList = None

async def fetch_manga(manga_id: int) -> Manga:
    """
    Used to fetch a manga object by id.
    Args:
        manga_id ( int ): manga id, as in the url

    Returns:
        manga ( aiomangadex.Manga ): Manga Instance
    """
    async with _session.get(f'https://mangadex.org/api/manga/{manga_id}') as resp:
        response = await resp.json()
    chapters = []
    for key, value in response.get('chapter').items():
        chapters.append(Chapter(id=key, **dict(value), session=_session))
    chapters.reverse()
    return Manga(**dict(response.get('manga')), chapters=ChapterList(chapters), id=manga_id, session=_session)