import pytz
from datetime import datetime

def now(zone_name='UTC'):
    """
    Returns the current datetime object for a specific timezone.
    Usage: liveclock.now('Asia/Dhaka')
    """
    try:
        target_zone = pytz.timezone(zone_name)
        return datetime.now(target_zone)
    except Exception:
        # Fallback to local system time if timezone is invalid
        return datetime.now()

def zone(zone_name='UTC'):
    """
    An alias for now() to allow liveclock.zone() usage.
    Usage: liveclock.zone('Asia/Dhaka')
    """
    return now(zone_name)

def year(zone_name='UTC'):
    """
    Returns the current year as an integer.
    Usage: liveclock.year('UTC') -> 2025
    """
    return now(zone_name).year

def timestamp():
    """
    Returns a clean string format of the current local time.
    Usage: liveclock.timestamp() -> '2025-12-29 11:25:01'
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


