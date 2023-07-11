from gcaltools.config import DATE_FORMAT
from datetime import datetime, timedelta


# UNUSED
def rfc3339_to_datetime(rfc3339_string):
    return datetime.fromisoformat(rfc3339_string)


def today_date():
    return datetime.now().strftime(DATE_FORMAT)


def next_date():
    return (datetime.now() + timedelta(days=6)).strftime(DATE_FORMAT)
