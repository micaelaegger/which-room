import datetime as dt

import discord
from discord.ext import tasks

from exceptions import ScheduleError
from schedule import TZ, build_message_for_day

# when the morning message is posted (07.00)
POST_TIME = dt.time(hour=7, minute=0, tzinfo=TZ)


class RoomBot(discord.Client):
    """Always-on Discord bot that posts the day's room at 07.00."""

    def __init__(self, ical_url: str, channel_id: int):
        super().__init__(
            intents=discord.Intents.default(),
            # don't let text from the schedule (e.g. "@everyone") ping anyone
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.ical_url = ical_url
        self.channel_id = channel_id

    async def setup_hook(self):
        """Runs once when the bot starts: starts the daily loop."""
        self.morning_post.start()

    async def on_ready(self):
        """Runs when the bot has connected to Discord."""
        print(f"Logged in as {self.user}")

    async def get_channel_to_post(self):
        """Returns the channel to post in.

        Raises discord.HTTPException if the channel can't be fetched.
        """
        # use the channel from the bot's cache, otherwise ask Discord for it
        return self.get_channel(self.channel_id) or await self.fetch_channel(
            self.channel_id
        )

    @tasks.loop(time=POST_TIME)
    async def morning_post(self):
        """Posts today's message. Stays quiet if there are no lessons.

        Catches all errors so the daily loop keeps running. If the schedule
        can't be fetched, a warning is posted in the channel instead.
        """
        try:
            today = dt.datetime.now(TZ).date()
            message = await build_message_for_day(self.ical_url, today)

            if message is None:
                return  # no lessons today, stay quiet

            channel = await self.get_channel_to_post()
            await channel.send(message)

        except ScheduleError as e:
            print(f"Could not fetch schedule: {e}")
            try:
                channel = await self.get_channel_to_post()
                await channel.send("⚠️ Kunde inte hämta schemat idag, kolla TimeEdit.")
            except discord.HTTPException as e:
                print(f"Could not send warning: {e}")

        except discord.HTTPException as e:
            print(f"Could not send message: {e}")

        except Exception as e:
            # safety net, keeps the loop alive on errors we didn't plan for
            print(f"Unexpected error: {e}")

    @morning_post.before_loop
    async def before_morning_post(self):
        """Waits until the bot is connected before the loop starts."""
        await self.wait_until_ready()
