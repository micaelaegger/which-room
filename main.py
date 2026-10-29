import os
import asyncio

from dotenv import load_dotenv
from icalendar import Calendar
from dataclasses import dataclass
from datetime import datetime, date
from zoneinfo import ZoneInfo


from schedule import fetch_ical, parse_lessons, lessons_for_day, format_message

TZ = ZoneInfo("Europe/Stockholm")


load_dotenv()
url = os.getenv("ICAL_URL")


async def main():
    data = await fetch_ical(url)
    lessons = parse_lessons(data)
    day = datetime.now(TZ).date()
    todays_lessons = lessons_for_day(lessons, day)
    message = format_message(todays_lessons)

    print(message)


asyncio.run(main())
