class MangadexException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self._msg = ''

class HttpException(MangadexException):
    def __init__(self, code):
        self.code = code

class MangaNotFound(MangadexException):
    def __init__(self, manga_id):
        self._msg = f"Could not find manga with id {manga_id}"
    def __str__(self):
        return self._msg

class UserNotFound(MangadexException):
    def __init__(self, user_id):
        self._msg = f"Couldn't find user {user_id}"
    def __str__(self):
        return self._msg