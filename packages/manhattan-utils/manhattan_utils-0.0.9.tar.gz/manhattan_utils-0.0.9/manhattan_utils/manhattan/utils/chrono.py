from datetime import datetime, timedelta, timezone

from flask import current_app
import pytz

__all__ = [
    'as_tz',
    'localize_datetime',
    'now_tz',
    'str_to_date',
    'str_to_datetime',
    'today_tz'
]


def as_tz(dt, tz=None):
    """Convert a date/time to the given timezone"""
    timezone = pytz.timezone(tz or current_app.config['TIMEZONE'])
    if dt.tzinfo:
        return dt.astimezone(timezone)
    return timezone.localize(dt)

def localize_datetime(dt, tz=None):
    """Convert a datetime to local time"""
    timezone = pytz.timezone(tz or current_app.config['TIMEZONE'])
    if dt.tzinfo:
        dt = dt.astimezone(timezone)
    else:
        # We assume that timezone naive datetimes are UTC
        dt = pytz.utc.localize(dt)
        dt = dt.astimezone(timezone)

    return dt

def now_tz(tz=None):
    """Return the date/time for the given timezone"""
    timezone = pytz.timezone(tz or current_app.config['TIMEZONE'])
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone)
    return now

def str_to_date(s):
    """Convert a string (YYYY-MM-DD) to a `datetime.date` instance"""
    return datetime.strptime(s, '%Y-%m-%d').date()

def str_to_datetime(s):
    """
    Convert a string (YYYY-MM-DD HH:MM:SS) to a `datetime.datetime instance`.
    """
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def today_tz(tz=None):
    """Return the date for the given timezone"""
    timezone = pytz.timezone(tz or current_app.config['TIMEZONE'])
    now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone)
    return now.date()

def utcnow():
    """A future compatible version of utc now"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
