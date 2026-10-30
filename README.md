# which-room

A small Discord bot that tells the class which room to go to every weekday morning. The schedule is fetched from TimeEdit (an iCal link).

Example messages (the bot writes in Swedish):

```
Godmorgon!
Idag har vi Databashantering i sal **B201**.
```

```
Godmorgon!
Vi byter sal under dagen:
09:00–12:00 Databashantering **B201**
13:00–15:00 Gästföreläsning **C218**
```

- If the class stays in the same room all day, the day's courses and the room are shown.
- If the room changes during the day, every lesson is listed with its time, course and room.
- If a lesson has no room in the schedule, it shows "sal saknas". If no lesson has a room, the message says to check TimeEdit.
- If there are no lessons, no message is sent.

## Two ways to run the bot

The repo has two versions of the bot. Both build the message the same way (with `build_message_for_day` in `schedule.py`), but they send it differently.

### 1. GitHub Actions + webhook (`post_today.py`), the one in use now

GitHub runs `post_today.py` automatically every weekday (see `.github/workflows/morning.yml`). The script sends the message through a Discord **webhook** and then exits.

- **Pro:** no computer or server needs to be running.
- If the schedule can't be fetched, it posts a warning in the channel. The GitHub run is then marked as failed, so you get an email.
- The settings are stored as **GitHub Secrets** (Settings → Secrets and variables → Actions):
  - `ICAL_URL`: the iCal link from TimeEdit
  - `DISCORD_WEBHOOK_URL`: the channel's webhook link (Channel settings → Integrations → Webhooks)

You can also run it manually from the **Actions** tab → *Morning post* → *Run workflow*. There you can enter a test date (`YYYY-MM-DD`) to see what the message looks like on a given day.

> **Note on time zones:** GitHub uses UTC. `0 6 * * 1-5` means 06:00 UTC, which is **07:00 in Swedish winter time** but **08:00 in summer time**. To post at 07:00 in summer, change it to `0 5 * * 1-5` when the clocks change.

### 2. Always-on Discord bot (`main.py` + `bot.py`)

A "real" Discord bot that logs in and keeps running. Every day at 07:00 Swedish time it sends the message. This version is kept in the repo but is not used right now. This version can be extended with more features, such as commands. If it can't fetch the schedule, it posts a warning in the channel.

## Installation (to run locally)

Requires Python 3.13 or later.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a file called `.env` in the project folder. Git ignores it, so your secret keys never end up on GitHub.

```
ICAL_URL=https://cloud.timeedit.net/...ics
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# only needed for the Discord bot version (main.py)
DISCORD_TOKEN=your-bot-token
CHANNEL_ID=123456789012345678
```

### Running the webhook version

`post_today.py` doesn't read `.env` itself, so the variables have to be set in the terminal:

```bash
export $(grep -v '^#' .env | xargs)
python post_today.py

# try another date:
TEST_DATE=2026-11-09 python post_today.py
```

### Running the Discord bot version

```bash
python main.py
```

## Files

| File | What it does |
|---|---|
| `schedule.py` | Fetches the schedule, turns it into `Lesson` objects, picks out the day's lessons and builds the message. All the logic lives here. |
| `post_today.py` | Webhook version: sends today's message once and exits. Run by GitHub Actions. |
| `bot.py` | Discord bot version: the `RoomBot` class with a loop that posts at 07:00 every day. |
| `main.py` | Starts `RoomBot` with the settings from `.env`. |
| `exceptions.py` | A custom error type, `ScheduleError`, used when the schedule can't be fetched. |
| `.github/workflows/morning.yml` | Tells GitHub when to run `post_today.py`. |
