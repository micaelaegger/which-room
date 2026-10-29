import os
from datetime import date

import discord
from dotenv import load_dotenv

from schedule import fetch_ical, parse_lessons, lessons_for_day, format_message

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
ical_url = os.getenv("ICAL_URL")
channel_id = int(os.getenv("CHANNEL_ID"))

# Days to preview: course start, same room, different rooms
TEST_DAYS = [
    date(2026, 11, 9),
    date(2026, 11, 16),
    date(2026, 11, 11),
]

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print(f"Logged in as {client.user}, sending test messages...")
    channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)

    data = await fetch_ical(ical_url)
    lessons = parse_lessons(data)

    for day in TEST_DAYS:
        days_lessons = lessons_for_day(lessons, day)
        if not days_lessons:
            await channel.send(f"🧪 *Test {day}: inga lektioner*")
            continue

        await channel.send(f"🧪 *Test {day}:*\n{format_message(days_lessons, lessons)}")

    print("Done!")
    await client.close()  # log out when finished


client.run(token)
