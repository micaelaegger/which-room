import os
import asyncio

from dotenv import load_dotenv
from icalendar import Calendar
from dataclasses import dataclass
from datetime import datetime


from schedule import fetch_ical, parse_lessons


load_dotenv()
url = os.getenv("ICAL_URL")


async def main():
    data = await fetch_ical(url)
    lessons = parse_lessons(data)


asyncio.run(main())
