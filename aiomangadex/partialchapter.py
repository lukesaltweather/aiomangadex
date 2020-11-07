from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .base import MangadexBase
from .group import Group
from .language import Language

@dataclass
class PartialChapter(MangadexBase):
    id: int = None
    hash: str = None
    manga = None
    volume: float = None
    chapter: float = None
    title: str = None
    groups: List[Group] = field(default_factory=list)
    language: Language = Language.NoLang()
    timestamp: datetime = 0
    comments: int = 0

    def __post_init__(self):
        self.timestamp = datetime.fromtimestamp(self.timestamp)

    def __hash__(self):
        return self.hash



class ChapterMixin:
    pass