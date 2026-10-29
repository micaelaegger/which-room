class ScheduleError(Exception):
    """Schedule could not be fetched. E.g networkerror or timeouterror"""


class InvalidLinkError(ScheduleError):
    """Ical-link does not work and need to be changed"""
