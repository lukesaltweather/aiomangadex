import asyncio
import io
import json
import typing

import aiohttp

from urllib.parse import quote as _uriquote

class Route:
    BASE = 'https://mangadex.org/api/v2/'

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

class MangadexSession:
    def __init__(self, session=None, loop=None, *, username = None, password = None):
        self._loop = loop or asyncio.get_running_loop()
        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession()
        self._ready = asyncio.Semaphore(0)
        self._loop.create_task(self._login(user=username, password=password))

    async def _request(self, route: Route):
        # handle Ratelimits
        async with self._session.request(route.method, route.url, headers=route.headers, data=route.data) as resp:
            data = await resp.json()
        if data['code'] in (200,):
            return data['data']

    async def _login(self, *, user, password):
        route = "https://mangadex.org/ajax/actions.ajax.php?function=login"
        headers= {"X-Requested-With": "XMLHttpRequest", "Origin": "https://mangadex.org", "Referer": "https://mangadex.org/login"}
        async with self._session.post(route, data={"login_username": user, "login_password": password, "two_factor": None}, headers=headers) as resp:
            pass
        self._ready.release()

    def get_manga(self, manga_id, include_partial_chapters = False):
        if include_partial_chapters:
            return self._request(Route("GET", f"manga/{manga_id}", include='chapters'))
        return self._request(Route("GET", f"manga/{manga_id}"))

    def get_manga_covers(self, manga_id):
        return self._request(Route("GET", f"manga/{manga_id}/covers"))

    def get_partial_chapters(self, manga_id):
        return self._request(Route("GET", f"manga/{manga_id}/chapters"))

    def get_chapter(self, chapter_id_or_hash: int):
        return self._request(Route("GET", f"chapters/{chapter_id_or_hash}"))

    def get_group(self, group_id: int, *, include_chapter: bool = None):
        if not include_chapter:
            return self._request(Route("GET", f"group/{group_id}"))
        return self._request(Route("GET", f"group/{group_id}?include=chapters"))

    def get_group_partial_chapters(self, group_id: int, page: int = 0, limit: int = 100):
        return self._request(Route("GET", f"group/{group_id}?p={page}&limit={limit}"))

    def get_user(self, user_id, *, include_chapters: bool = None):
        if not include_chapters:
            return self._request(Route("GET", f"/users/{user_id}"))
        return self._request(Route("GET", f"user/{user_id}?include=chapters"))

    def get_user_followed_manga(self, user_id: typing.Union[int, str] = "me"):
        return self._request(Route("GET", f"user/{user_id}/followed-manga"))

    def get_user_chapters(self):
        pass

    def get_user_settings(self):
        pass

    def get_user_followed_updates(self):
        pass

    def get_user_ratings(self):
        pass

    def get_user_manga_info(self):
        pass

    def get_all_tags(self):
        pass

    def get_tag(self):
        pass

    def set_marker(self, chapter: typing.List[int], set_to: bool = True):
        return self._request(Route("POST", "user/me/marker", {"Content-Type": "application/json"}, read=set_to, body = json.dumps(chapter)))

    def upload_chapter(self, file: io.BytesIO, *, filename='chapter.zip', manga_id: int, chapter_title=None, volume=None, chapter_number: float, group_id: int, group_id_2: int = None, group_id_3: int = None, lang_id: str):
        data = aiohttp.FormData()
        data.add_field('file',
                       file,
                       filename=filename,
                       content_type='application/x-zip-compressed')
        data.add_field('manga_id', manga_id)
        data.add_field('chapter_name', chapter_title)
        data.add_field('volume_number', volume)
        data.add_field('chapter_number', chapter_number)
        data.add_field('group_id', group_id)
        data.add_field('group_id_2', group_id_2)
        data.add_field('group_id_3', group_id_3)
        data.add_field('lang_id', lang_id)
        await self._request(Route("POST", "https://mangadex.org/ajax/actions.ajax.php?function=chapter_upload", data=data, headers={"Accept-Encoding":"gzip, deflate, br", "X-Requested-With": "XMLHttpRequest", "Content-Type": "multipart/form-data", "Connection":"keep-alive"}))

    def wait_until_ready(self):
        return self._ready.acquire()
