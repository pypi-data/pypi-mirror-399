import pytz
from datetime import datetime

def now(zone='UTC'):
    """Returns the current time for a given timezone."""
    try:
        target_zone = pytz.timezone(zone)
        return datetime.now(target_zone)
    except Exception:
        # Fallback to local time if zone is invalid
        return datetime.now()

def year(zone='UTC'):
    """Returns the current year for a given timezone."""
    return now(zone).year

def timestamp():
    """Returns a standard formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

