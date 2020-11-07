import asyncio
import difflib
import io
import json

import aiohttp

from dataclasses import dataclass
from typing import List, Union

from aiomangadex.chapter import Chapter, ChapterList
from aiomangadex.session import _session


@dataclass(frozen=True)
class Manga:
    """Represents part of result of https://mangadex.org/api/manga/{id}

    Attributes:
        id ( int ): Manga id
        cover_url ( string ): URL to manga cover
        description ( str )
        rating ( dict)
        alt_names ( List[ str ] )
        title ( str )
        artist ( str )
        author ( str )
        status ( int )
        genres ( List[ str ] )
        last_chapter ( int )
        lang_name ( str )
        lang_flag ( str )
        hentai ( bool )
        links ( dict )
        chapters ( ChapterList )
        session ( aiohttp.ClientSession )

    Warnings:
        Some of the chapter data is *not* included in the initial fetch, meaning you'll have to fetch the missing things in :class:`aiomangadex.Chapter`.
    """
    id: int
    cover_url: str
    description: str
    rating: dict
    demographic: int
    last_volume: int
    last_updated: int
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
    related: List
    views: int
    follows: int
    covers: List[str]
    comments: int
    chapters: ChapterList
    session: aiohttp.ClientSession = None

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