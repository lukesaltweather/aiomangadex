from dataclasses import dataclass

@dataclass
class MangadexBase:
    id: int = None

    @classmethod
    def from_json(cls, json):
        return cls(**dict(json))