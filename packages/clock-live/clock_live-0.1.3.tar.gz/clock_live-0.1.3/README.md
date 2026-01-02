### 0. Hello

This is a library thats so useful you dont need an hourglass and a clock and a calendar if you're a programmer

You have might have seen it in pypi, but its essential if you don't have a clock

### 1. What is clock-live?

clock-live is not your clock app, its a library, not just any library, it is for checking the date, time, timezone for programmers, you don't need to use this syntax anymore

```python
from datetime import datetime
now = datetime.now()
print(f"The date and time is: {now}")
```

Instead use this syntax

#### 1. a. Checking the time

```python
import liveclock

today = liveclock.now()

print(f"You are in: {liveclock.LOCAL_ZONE}")
print(f"Local time: {today}")
```

##### 1. a. a. Formatting the time

Don't worry! We used the datetime library

To format:

```python
import liveclock

today = liveclock.now()
today_f = today.strftime("%Y-%m-%d %H:%M:%S")

print(f"You are in: {liveclock.LOCAL_ZONE}")
print(f"Local time: {today_f}")
```

for date only

```python
import liveclock

today = liveclock.now()
today_date = today.date()

print(f"You are in: {liveclock.LOCAL_ZONE}")
print(f"Local time: {today_date}")
```

for time only:

```python
import liveclock

today = liveclock.now()
today_time = today.time()

print(f"You are in: {liveclock.LOCAL_ZONE}")
print(f"Local time: {today_time}")
```

#### 1. b. Timezone

```python
import liveclock

# No args = Your local zone (e.g., America/New_York)
my_tz = liveclock.zone() 
print(f"Object: {my_tz}")
print(f"Name: {my_tz.zone}")
```

#### 1. c. Timer

```python
import liveclock
from datetime import timedelta

# 1.1 Create a target (5 seconds from now)
target_time = liveclock.now() + timedelta(seconds=5)

# 1.2 Initialize
t = liveclock.Timer(target_time)

# 1.3 Wait for the end
print("Countdown started...")
t.wait_until_finished() 
```

### 2. Installation

To use this, type:

```bash
pip install clock-live
```

if there is updates:

```bash
pip install -u clock-live
```

### 3. After reading

You can close, but only if you memorized the codes given from 1. a to 1. c

If you cant memorize, follow 2. Installation, and 1. a to 1. c