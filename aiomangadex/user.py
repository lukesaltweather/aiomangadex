from dataclasses import dataclass
from datetime import datetime

from .base import MangadexBase
from .chapterlist import ChapterList

@dataclass(frozen=True)
class User(MangadexBase):
    username: str = ''
    levelId: int = None
    joined: datetime = None
    lastSeen: datetime = None
    website: str = ''
    biography: str = ''
    views: int = None
    uploads: int = None
    premium: bool = None
    mdAtHome: int = None
    avatar: str = ''
    chapters: ChapterList = None

    @classmethod
    def from_json(cls, json, http):
        joined = datetime.fromtimestamp(json.pop('joined'))
        lastSeen = datetime.fromtimestamp(json.pop('lastSeen'))
        chli = ChapterList.from_partial_chapters(json.pop('chapters'))
        return cls(joined=joined, lastSeen=lastSeen, http=http, chapters=chli, **json)