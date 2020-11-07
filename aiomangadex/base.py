class MangadexBase:
    @classmethod
    def from_json(cls, json):
        return cls(**dict(json))