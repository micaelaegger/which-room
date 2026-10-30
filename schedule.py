from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

import aiohttp
from icalendar import Calendar

from exceptions import ScheduleError

TZ = ZoneInfo("Europe/Stockholm")


async def fetch_ical(url) -> bytes:
    """Downloads the schedule from TimeEdit and returns it as raw bytes.

    Raises ScheduleError on network errors, bad responses or timeout (10 s).
    """
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
    """One lesson from the schedule."""

    start: datetime
    end: datetime
    location: str
    course: str
    lecturer: str


def parse_lessons(data: bytes) -> list[Lesson]:
    """Turns the raw schedule into a list of Lesson objects.

    All-day events are skipped. Raises ScheduleError if the data
    is not a valid calendar (e.g. TimeEdit sent an HTML page).
    """
    try:
        # converts bytes to a calendar object
        cal = Calendar.from_ical(data)
    except ValueError as e:
        raise ScheduleError(f"Schedule is not a valid calendar: {e}") from e

    lessons = []

    for event in cal.walk("VEVENT"):
        start = event.decoded("DTSTART")

        # all-day events (e.g. an exam day) only have a date, no time: skip them
        if not isinstance(start, datetime):
            continue

        start = start.astimezone(TZ)
        end = event.decoded("DTEND").astimezone(TZ)
        # a missing room becomes "" (instead of the text "None"), same as an empty room
        location = str(event.get("LOCATION", "")).strip()
        summary = str(event.get("SUMMARY", ""))

        # TimeEdit writes the summary as "..., lecturer, course"
        parts = summary.split(", ")
        if len(parts) >= 2:
            lecturer = parts[-2].strip()
            course = parts[-1].strip()
        else:
            # unexpected format: use the whole summary as course name instead of crashing
            lecturer = ""
            course = summary.strip()

        # TimeEdit labels guest lectures as "Aktivitet", assigning a clearer name
        if lecturer == "Gästföreläsare":
            course = "Gästföreläsning"

        lesson = Lesson(start, end, location, course, lecturer)
        lessons.append(lesson)

    return lessons


def lessons_for_day(lessons: list[Lesson], day: date) -> list[Lesson]:
    """Returns the lessons that start on the given day."""
    todays_lessons = []

    for lesson in lessons:
        if day == lesson.start.date():
            todays_lessons.append(lesson)

    return todays_lessons


def format_message(todays_lessons: list[Lesson]) -> str:
    """Builds the morning message. Expects todays_lessons to be non-empty.

    Lessons without a room are shown as "sal saknas".
    """
    # a set only keeps unique values, so each room appears once
    rooms = {lesson.location for lesson in todays_lessons}

    # today's courses, each once, in the order they appear
    courses = []
    for lesson in todays_lessons:
        if lesson.course not in courses:
            courses.append(lesson.course)

    # e.g. "Databashantering och Gästföreläsning"
    course_names = " och ".join(courses)

    lines = ["Godmorgon!"]

    if rooms == {""}:
        # no lesson today has a room in the schedule
        lines.append(
            f"Idag har vi {course_names}. Salen står inte i schemat, kolla TimeEdit."
        )
    elif len(rooms) == 1:
        lines.append(
            f"📍 Idag har vi {course_names} i sal **{todays_lessons[0].location}**."
        )
    else:
        # also used when only some lessons are missing a room,
        # since that lesson might be somewhere else
        lines.append("Vi byter sal under dagen:")
        for lesson in todays_lessons:
            location = lesson.location or "sal saknas"
            lines.append(
                f"{lesson.start:%H:%M}–{lesson.end:%H:%M} {lesson.course} **{location}**"
            )

    return "\n".join(lines)


async def build_message_for_day(ical_url: str, day: date) -> str | None:
    """Fetches the schedule and returns the message for the given day,
    or None if there are no lessons that day.

    Raises ScheduleError if the schedule can't be fetched or read.
    """
    data = await fetch_ical(ical_url)
    all_lessons = parse_lessons(data)
    todays_lessons = lessons_for_day(all_lessons, day)

    if not todays_lessons:
        return None

    return format_message(todays_lessons)
