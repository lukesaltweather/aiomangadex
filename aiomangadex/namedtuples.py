from collections import namedtuple

Cover = namedtuple('Cover', ('volume', 'url'))

FollowedManga = namedtuple('FollowedManga', ('userId', 'mangaId', 'followType', 'volume', 'chapter', 'rating'))

