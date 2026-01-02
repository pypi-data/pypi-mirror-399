from .core import now
from .zones import zone, timezone
from .locator import get_local_tz
from .countdown import Timer

# Constant for user reference
LOCAL_ZONE = get_local_tz()

__all__ = ['now', 'zone', 'timezone', 'Timer', 'LOCAL_ZONE']
