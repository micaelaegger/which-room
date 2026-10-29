import aiohttp
from icalendar import Calendar
from dataclasses import dataclass
from datetime import datetime, date
from zoneinfo import ZoneInfo

from exceptions import ScheduleError

TZ = ZoneInfo("Europe/Stockholm")


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


@dataclass
class Lesson:
    start: datetime
    end: datetime
    location: str
    course: str
    lecturer: str


def parse_lessons(data: bytes) -> list[Lesson]:
    # converts bytes to a calendar object
    cal = Calendar.from_ical(data)

    lessons = []

    for event in cal.walk("VEVENT"):
        start = event.decoded("DTSTART").astimezone(TZ)
        end = event.decoded("DTEND").astimezone(TZ)
        location = str(event.get("LOCATION"))
        summary = str(event.get("SUMMARY"))

        parts = summary.split(", ")
        lecturer = parts[-2].strip()
        course = parts[-1].strip()

        # TimeEdit labels guest lectures as "Aktivitet", assigning a clearer name
        if lecturer == "Gästföreläsare":
            course = "Gästföreläsning"

        lesson = Lesson(start, end, location, course, lecturer)
        lessons.append(lesson)

    return lessons


def lessons_for_day(lessons: list[Lesson], day: date) -> list[Lesson]:
    todays_lessons = []

    for lesson in lessons:
        if day == lesson.start.date():
            todays_lessons.append(lesson)

    return todays_lessons


def format_message(lessons: list[Lesson]) -> str:
    if not lessons:
        return

    # set of unique rooms, duplicates are removed, is a list
    rooms = {lesson.location for lesson in lessons}

    if len(rooms) == 1:
        room = lessons[0].location
        return f"☀️ Godmorgon! Idag är vi i sal **{room}** hela dagen!"

    lines = ["☀️ Godmorgon! Dagens salar:"]

    for lesson in lessons:
        lines.append(
            f"{lesson.start:%H:%M}–{lesson.end:%H:%M} {lesson.course} **{lesson.location}**"
        )

    return "\n".join(lines)
