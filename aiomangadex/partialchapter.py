from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .base import MangadexBase
from .group import Group
from .language import Language

@dataclass(frozen=True)
class PartialChapter(MangadexBase):
    id: int = None
    hash: str = None
    manga = None
    volume: float = None
    chapter: float = None
    title: str = None
    groups: List[Group] = field(default_factory=list)
    language: Language = Language.NoLang()
    timestamp: datetime = None
    comments: int = 0

    def __hash__(self):
        return self.hash

class ChapterMixin:
    pass