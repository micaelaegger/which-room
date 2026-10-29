import os

from dotenv import load_dotenv

from bot import RoomBot

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
ical_url = os.getenv("ICAL_URL")
channel_id = os.getenv("CHANNEL_ID")

# Fail early with a clear message if something is missing in .env
if not token or not ical_url or not channel_id:
    raise SystemExit("Missing DISCORD_TOKEN, ICAL_URL or CHANNEL_ID in .env")

bot = RoomBot(ical_url, int(channel_id))
bot.run(token)  # starts the bot - no asyncio.run needed, discord.py handles it
