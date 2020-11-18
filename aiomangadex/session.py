import asyncio
import io
import json
import typing
import weakref

import aiohttp

from urllib.parse import quote as _uriquote

from .exceptions import HttpException
from .manga import Manga
from .user import User
from .chapter import Chapter
from .group import Group

class AsyncLeakyBucket:
    #stolen from stackoverflow as im a lazy fuck
    #https://stackoverflow.com/a/48685838
    def __init__(self, max_tasks: int, time_period: float = 60, loop: asyncio.events=None):
        self._delay_time = time_period / max_tasks
        self._sem = asyncio.BoundedSemaphore(max_tasks)
        self._loop = loop or asyncio.get_event_loop()
        self._loop.create_task(self._leak_sem())

    async def _leak_sem(self):
        """
        Background task that leaks semaphore releases based on the desired rate of tasks per time_period
        """
        while True:
            await asyncio.sleep(self._delay_time)
            try:
                self._sem.release()
            except ValueError:
                pass

    async def __aenter__(self) -> None:
        await self._sem.acquire()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass

class Route:
    BASE = 'https://mangadex.org/api/v2/'

    __slots__ = ('path', 'method', 'headers', 'data', 'url')

    def __init__(self, method, path, headers=None, data=None, **parameters):
        self.path = path
        self.method = method
        self.headers = headers
        self.data = data
        url = (self.BASE + self.path)
        if parameters:
            s = '?'
            for k, v in parameters.items():
                s = f"{s}{_uriquote(k)}={_uriquote(v)}&"
            self.url = f"{url}{s}"
        else:
            self.url = url

class Cache:
    __slots__ = ('user_cache', 'manga_cache', 'chapter_cache', 'group_cache')

    def __init__(self):
        self.user_cache = {}
        self.manga_cache = {}
        self.chapter_cache = {}
        self.group_cache = {}

    def get_user(self, id):
        return self.user_cache.get(id, None)

    def get_manga(self, id):
        return self.manga_cache.get(id, None)

    def get_chapter(self, id):
        return self.chapter_cache.get(id, None)

    def get_group(self, id):
        return self.group_cache.get(id, None)


class MangadexSession:

    __slots__ = ('_loop', '_session', '_ready', '_lock', '_cache')

    def __init__(self, session=None, loop=None, login: bool = False, *, username = None, password = None):
        self._loop = loop or asyncio.get_running_loop()
        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()
        self._ready = asyncio.Semaphore(0)
        self._lock = AsyncLeakyBucket(1, 1.0)
        # self._cache = Cache()
        if login:
            self._loop.create_task(self._login(user=username, password=password))

    async def _request(self, route: Route):
        async with self._lock:
            async with self._session.request(route.method, route.url, headers=route.headers, data=route.data) as resp:
                data = await resp.json()
            if data['code'] == 200:
                return data['data']
            raise HttpException(code=data['code'])

    async def _login(self, *, user, password):
        route = "https://mangadex.org/ajax/actions.ajax.php?function=login"
        headers= {"X-Requested-With": "XMLHttpRequest", "Origin": "https://mangadex.org", "Referer": "https://mangadex.org/login"}
        async with self._session.post(route, data={"login_username": user, "login_password": password, "two_factor": None}, headers=headers) as resp:
            pass
        self._ready.release()

    async def _logout(self):
        raise NotImplementedError

    def fetch_manga(self, manga_id, include_partial_chapters = False):
        if include_partial_chapters:
            return self._request(Route("GET", f"manga/{manga_id}", include='chapters'))
        return self._request(Route("GET", f"manga/{manga_id}"))

    def fetch_manga_covers(self, manga_id):
        return self._request(Route("GET", f"manga/{manga_id}/covers"))

    def fetch_partial_chapters(self, manga_id):
        return self._request(Route("GET", f"manga/{manga_id}/chapters"))

    def fetch_chapter(self, chapter_id_or_hash: int):
        return self._request(Route("GET", f"chapter/{chapter_id_or_hash}"))

    def fetch_group(self, group_id: int, *, include_chapter: bool = None):
        if not include_chapter:
            return self._request(Route("GET", f"group/{group_id}"))
        return self._request(Route("GET", f"group/{group_id}?include=chapters"))

    def fetch_group_partial_chapters(self, group_id: int, page: int = 0, limit: int = 100):
        return self._request(Route("GET", f"group/{group_id}?p={page}&limit={limit}"))

    def fetch_user(self, user_id, *, include_chapters: bool = None):
        if not include_chapters:
            return self._request(Route("GET", f"/users/{user_id}"))
        return self._request(Route("GET", f"user/{user_id}?include=chapters"))

    def fetch_user_followed_manga(self, user_id: typing.Union[int, str] = "me"):
        return self._request(Route("GET", f"user/{user_id}/followed-manga"))

    def fetch_user_chapters(self, user_id = 'me', page = 0, limit = 100):
        #auth
        return self._request(Route("GET", f"user/{user_id}/chapters", p=page, limit=limit))

    def fetch_user_settings(self, user_id = 'me'):
        #auth
        return self._request(Route("GET", f"user/{user_id}/settings"))

    def fetch_user_followed_updates(self, user_id = 'me', page = 1, type = 0, hentai = 0, delayed = False):
        #auth
        return self._request(Route("GET", f"user/{user_id}/followed-updates", p=page, type=type, hentai=hentai, delayed=delayed))

    def fetch_user_ratings(self, user_id):
        #auth
        return self._request(Route("GET", f"user/{user_id}/ratings"))

    def fetch_user_manga_info(self, user_id, manga_id):
        #auth
        return self._request(Route("GET", f"user/{user_id}/manga/{manga_id}"))

    def fetch_all_tags(self):
        return self._request(Route("GET", f"tag"))

    def fetch_tag(self, tag_id):
        return self._request(Route("GET", f"tag/{tag_id}"))

    def set_marker(self, chapter: typing.List[int], set_to: bool = True):
        return self._request(Route("POST", "user/me/marker", {"Content-Type": "application/json"}, read=set_to, body = json.dumps(chapter)))

    def upload_chapter(self, file: io.BufferedIOBase, *, filename, manga_id: int, chapter_title='', volume: float = '', chapter_number: float, lang_id: int, group_id: int, group_id_2: int= '', group_id_3: int = ''):
        data = aiohttp.FormData()
        data.add_field('manga_id', str(manga_id))
        data.add_field('volume_number', str(volume))
        data.add_field('chapter_number', str(chapter_number))
        data.add_field('chapter_name', str(chapter_title))
        data.add_field('lang_id', str(lang_id))
        data.add_field('group_id', str(group_id))
        data.add_field('file',
                       file, filename=filename)
        data.add_field('group_id_2', str(group_id_2))
        data.add_field('group_id_3', str(group_id_3))
        return self._session.post("https://mangadex.org/ajax/actions.ajax.php?function=chapter_upload", data=data, headers={"Connection":"keep-alive", "dnt": "1", "origin": "https://mangadex.org", "referer": f"https://mangadex.org/manga/{manga_id}", "x-requested-with": "XMLHttpRequest"})

    def wait_until_ready(self):
        # rewrite using a future
        return self._ready.acquire()
