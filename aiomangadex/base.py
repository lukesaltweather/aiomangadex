from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class MangadexBase:
    id: int = None
    http: Any = None

    @classmethod
    @abstractmethod
    def from_json(cls, json, http):
        pass