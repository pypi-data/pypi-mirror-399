import pytz
from datetime import datetime
from .locator import get_local_tz

def now(tz_string=None):
    """Returns current datetime. Defaults to local if tz_string is None."""
    if tz_string is None:
        tz_string = get_local_tz()
    target_tz = pytz.timezone(tz_string)
    return datetime.now(target_tz)

# Alias for convenience
timezone = zone
