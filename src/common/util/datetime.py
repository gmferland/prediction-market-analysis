from datetime import datetime


def to_timestamp(dt: datetime):
    """Convert a datetime to Unix epoch."""
    return int(dt.timestamp())
