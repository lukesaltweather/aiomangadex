import asyncio

from typing import Union

from .session import MangadexSession
from .chapter import Chapter
from .manga import Manga
from .user import User
from .group import Group
from .chapterlist import ChapterList
from .namedtuples import Cover

class MangadexClient:

    __slots__ = ('http', '__dict__')

    def __init__(self, cache, *, user, password):
        self.http = MangadexSession(username=user, password=password, login=True)

    async def fetch_manga(self, manga_id: int, include_chapters=False):
        res = await self.http.fetch_manga(manga_id, include_partial_chapters=include_chapters)
        return Manga.from_json(json=res, http=self.http)

    async def fetch_manga_covers(self, manga_id: int):
        res = await self.http.fetch_manga_covers(manga_id)
        return [Cover(volume=a, url=b) for a, b in res.items()]

    async def fetch_partial_chapters(self, manga_id: int):
        res = await self.http.fetch_partial_chapters(manga_id)
        return ChapterList.from_partial_chapters(res)

    async def fetch_chapter(self, chapter: Union[str, int]):
        data  = await self.http.fetch_chapter(chapter)
        return Chapter.from_json(data, self.http)

    async def fetch_group(self, group_id: int, include_chapters: bool = True):
        data = await self.http.fetch_group(id, include_chapter=include_chapters)
        return Group.from_json(data, self.http)

    async def fetch_group_partial_chapters(self, group_id: int):
        data = await self.http.fetch_group_partial_chapters(group_id)
        return ChapterList.from_partial_chapters(data)

    async def fetch_user(self, id: Union[int, str], include_chapters: bool = True):
        data = await self.http.fetch_user(id, include_chapters=include_chapters)
        return User.from_json(data, http=self.http)

    async def fetch_user_followed_manga(self, user_id: Union[str, int] = 'me'):
        pass

    async def fetch_user_chapters(self, user_id: Union[str, int] = 'me', max_pages: int = 50):
        raise NotImplementedError('Complete ChapterIterator')
        data = await self.http.fetch_user_chapters(user_id)
        return ChapterList.from_partial_chapters(data)

    async def fetch_user_settings(self):
        pass

    async def fetch_user_followed_updates(self):
        pass

    async def fetch_user_ratings(self):
        pass

    async def fetch_user_manga_info(self):
        pass

    async def fetch_all_tags(self):
        pass

    async def fetch_tag(self):
        pass

    async def set_marker(self):
        pass

    async def upload_chapter(self, file, *, filename: str = 'chapter.zip', manga_id: int, chapter_title: str = '', volume: float = '', chapter_number: float, lang_id: int, group_id: int, group_id_2: int= '', group_id_3: int = ''):
        return self.http.upload_chapter(file, filename=filename, manga_id=manga_id, chapter_title=chapter_title, volume=volume, chapter_number=chapter_number, lang_id=lang_id, group_id=group_id, group_id_2=group_id_2, group_id_3=group_id_3)

