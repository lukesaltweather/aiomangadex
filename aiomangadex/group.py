from collections import namedtuple
from dataclasses import dataclass
from datetime import date, datetime
from typing import List

from .base import MangadexBase
from .language import Language


PartialUser = namedtuple('PartialUser', ('id', 'name'))

@dataclass(frozen=True)
class Group(MangadexBase):
    id: int = None
    name: str = None
    altNames: str = None
    language: Language = None
    leader: PartialUser = None
    members: List[PartialUser] = None
    description: str = None
    website: str = None
    discord: str = None
    ircServer: str = None
    ircChannel: str = None
    email: str = None
    founded: date = None
    likes: int = None
    follows: int = None
    views: int = None
    chapters: int = None
    threadId: int = None
    threadPosts = None
    isLocked: bool = None
    isInactive: bool = None
    delay: int = None
    lastUpdated: datetime = None
    banner: str = None

    @classmethod
    def from_json(cls, json, http):
        pass