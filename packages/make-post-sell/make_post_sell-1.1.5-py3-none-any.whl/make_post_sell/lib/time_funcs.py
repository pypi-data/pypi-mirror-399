from datetime import datetime
from ago import human


def timestamp_to_datetime(timestamp):
    """Accepts a milliseconds timestamp integer and returns a datetime"""
    return datetime.fromtimestamp(timestamp / 1000.0)


def timestamp_to_ago_string(timestamp):
    """Accepts a timestamp and returns a human readable string"""
    return human(timestamp_to_datetime(timestamp), 2, abbreviate=True)
