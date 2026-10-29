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

    # Test days: course start, same room, different rooms, no lessons
    test_days = [
        date(2026, 11, 9),
        date(2026, 11, 16),
        date(2026, 11, 11),
        date(2026, 11, 7),
    ]

    for day in test_days:
        print(f"--- {day} ---")
        todays_lessons = lessons_for_day(lessons, day)

        if not todays_lessons:
            print("(inga lektioner, inget meddelande skickas)")
            continue

        print(format_message(todays_lessons, lessons))
        print()


asyncio.run(main())
