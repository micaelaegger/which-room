import asyncio
import datetime
import os

import aiohttp

from exceptions import ScheduleError
from schedule import TZ, build_message_for_day


async def send_to_discord(webhook_url: str, message: str):
    """Sends a message to the Discord channel through the webhook.

    Raises aiohttp.ClientResponseError if Discord doesn't accept it.
    """
    payload = {
        "content": message,
        # don't let text from the schedule (e.g. "@everyone") ping anyone
        "allowed_mentions": {"parse": []},
    }
    async with (
        aiohttp.ClientSession() as session,
        session.post(webhook_url, json=payload) as response,
    ):
        response.raise_for_status()


async def main():
    """Sends today's message (or TEST_DATE's) to Discord, once.

    If the schedule can't be fetched, a warning is sent instead and the
    error is raised again, so the GitHub run fails and you get an email.
    """
    ical_url = os.environ["ICAL_URL"]
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

    # TEST_DATE lets you preview another day (e.g. 2026-11-09) when running manually
    test_date = os.getenv("TEST_DATE")
    if test_date:
        day = datetime.date.fromisoformat(test_date)
    else:
        day = datetime.datetime.now(TZ).date()

    try:
        message = await build_message_for_day(ical_url, day)
    except ScheduleError:
        await send_to_discord(
            webhook_url, "⚠️ Kunde inte hämta schemat idag, kolla TimeEdit."
        )
        # raise the error again so the GitHub run is marked as failed and you get an email
        raise

    if message is None:
        print(f"No lessons on {day}, nothing sent")
        return

    await send_to_discord(webhook_url, message)
    print(f"Message for {day} sent")


# Only run main() when the file is started directly (python post_today.py),
# not when another file imports it
if __name__ == "__main__":
    asyncio.run(main())
