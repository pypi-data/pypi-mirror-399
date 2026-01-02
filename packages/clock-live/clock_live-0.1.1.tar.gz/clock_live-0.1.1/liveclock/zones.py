import pytz
from .locator import get_local_tz

def zone(name=None):
    """
    Returns a pytz timezone object.
    If no name is provided, it auto-detects your location.
    """
    if name is None:
        name = get_local_tz()
    return pytz.timezone(name)

def timezone(name=None):
    """Alias for zone()."""
    return zone(name)
