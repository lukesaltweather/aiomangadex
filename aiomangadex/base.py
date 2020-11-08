from dataclasses import dataclass

from .session import MangadexSession

@dataclass(frozen=True)
class MangadexBase:
    id: int = None
    http: MangadexSession = None

    @classmethod
    def from_json(cls, json):
        return cls(**dict(json))