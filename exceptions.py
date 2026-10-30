class ScheduleError(Exception):
    """The schedule could not be fetched or read, e.g. network error, timeout
    or TimeEdit sent something that isn't a calendar."""
