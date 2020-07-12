import pytest
import asyncio
import aiohttp
import json
from aiomangadex import *

class MockClientSessionGet:
    def __init__(self, jayson):
        self.response = jayson
    async def json(self):
        return self.response
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(exc_tb)

@pytest.fixture
def mock_get(monkeypatch):
    with open('34198.json', 'r') as f:
        jm = json.load(f)
    def new_get(*args, **kwargs):
        return MockClientSessionGet(jm)
    monkeypatch.setattr(aiohttp.ClientSession, 'get', new_get)

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

def test_fetch_manga(event_loop, mock_get):
    ma = event_loop.run_until_complete(fetch_manga(34198, aiohttp.ClientSession()))
    assert ma.author == 'Uoyama'
    event_loop.run_until_complete(ma.close_session())