import os
from dotenv import load_dotenv
import asyncio
import aiohttp
from exceptions import ScheduleError

load_dotenv()
url = os.getenv("ICAL_URL")
# Kolla så att enc-variabel laddas


# Returns raw bytes (undecoded data, not str) - icalendar parses this directly.
async def fetch_ical(url) -> bytes:
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        # Opens session, a connection that makes HTTP-req.
        # "async with" closes the connection automatically when finished
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.get(url) as response,
        ):
            response.raise_for_status()
            data = await response.read()
    except (aiohttp.ClientError, TimeoutError) as e:
        raise ScheduleError(f"Could not get schedule: {e}") from e

    return data


# data = asyncio.run(fetch_ical(url))
