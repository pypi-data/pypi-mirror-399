import time
from .core import now

class Timer:
    def __init__(self, target_time):
        self.target = target_time

    def remaining(self):
        """Calculates time left based on the target's timezone."""
        current = now(str(self.target.tzinfo))
        diff = self.target - current
        return diff if diff.total_seconds() > 0 else 0

    def wait_until_finished(self, callback=None):
        """Blocks execution until the target time is reached."""
        while self.remaining() != 0:
            time.sleep(0.5)
        
        if callback:
            callback()
        else:
            print("Time's up!")
