import asyncio
import datetime
import os

import aiohttp

from schedule import TZ, fetch_ical, parse_lessons, lessons_for_day, format_message


async def main():
    ical_url = os.environ["ICAL_URL"]
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

    # TEST_DATE lets you preview another day (e.g. 2026-11-09) when running manually
    test_date = os.getenv("TEST_DATE")
    day = (
        datetime.date.fromisoformat(test_date)
        if test_date
        else datetime.datetime.now(TZ).date()
    )

    data = await fetch_ical(ical_url)
    lessons = parse_lessons(data)
    days_lessons = lessons_for_day(lessons, day)

    if not days_lessons:
        print(f"No lessons on {day}, nothing sent")
        return

    # Send the message to the channel through the webhook
    async with (
        aiohttp.ClientSession() as session,
        session.post(
            webhook_url, json={"content": format_message(days_lessons, lessons)}
        ) as response,
    ):
        response.raise_for_status()

    print(f"Message for {day} sent")


asyncio.run(main())
