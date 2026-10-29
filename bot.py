import datetime as dt

import discord
from discord.ext import tasks

from exceptions import ScheduleError
from schedule import TZ, fetch_ical, parse_lessons, lessons_for_day, format_message

# when the morning message is posted (07.00)
POST_TIME = dt.time(hour=23, minute=48, tzinfo=TZ)


class RoomBot(discord.Client):
    def __init__(self, ical_url: str, channel_id: int):
        super().__init__(intents=discord.Intents.default())
        self.ical_url = ical_url
        self.channel_id = channel_id

    async def setup_hook(self):
        # runs once when the bot starts: start the daily loop
        self.morning_post.start()

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def get_channel_to_post(self):
        # 07.00
        return self.get_channel(self.channel_id) or await self.fetch_channel(
            self.channel_id
        )

    @tasks.loop(time=POST_TIME)
    async def morning_post(self):
        # an uncaught error would stop the loop for good, so catch errors here
        try:
            data = await fetch_ical(self.ical_url)
            lessons = parse_lessons(data)
            todays_lessons = lessons_for_day(lessons, dt.datetime.now(TZ).date())

            if not todays_lessons:
                return  # no lessons today, stay quiet

            channel = await self.get_channel_to_post()
            await channel.send(format_message(todays_lessons, lessons))

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
        await self.wait_until_ready()  # don't post before the bot is connected
