async def _download_file(session: aiohttp.ClientSession, url: str) -> io.BytesIO:
    """Helper function for downloading.

    Args:
        session (aiohttp.ClientSession): active Session
        url (str): URL to image

    Returns:
        io.BytesIO: Buffer with Image
    """
    async with session.get(url) as response:
        assert response.status == 200
        return io.BytesIO(await response.read())
