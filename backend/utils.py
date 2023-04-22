import json
import re
from datetime import timedelta, datetime
from types import SimpleNamespace


def load_config_to_namespace(config_path):
    with open(config_path) as json_file:
        ns = json.load(json_file,
                       object_hook=lambda x: SimpleNamespace(**x))
    return ns


def load_config(config_path):
    with open(config_path) as json_file:
        data = json.load(json_file)
    return data


def parse_timedelta(s):
    match = re.match(r'(\d+)([mshw])', s)
    if not match:
        raise ValueError(f'Invalid timedelta string: {s}')
    num, unit = match.groups()
    num = int(num)
    if unit == 's':
        return timedelta(seconds=num)
    elif unit == 'm':
        return timedelta(minutes=num)
    elif unit == 'h':
        return timedelta(hours=num)
    elif unit == 'w':
        return timedelta(weeks=num)


def adjust_time(time_str):
    # Parse the time unit and value from the input string
    time_value = int(time_str[:-1])
    time_unit = time_str[-1]

    # Get the current date
    current_date = datetime.now().date()

    # Create a datetime object with zeroed time
    zeroed_time = datetime(current_date.year,
                           current_date.month,
                           current_date.day, 0, 0)

    # Adjust the time based on the input
    if time_unit == 'm':
        adjusted_time = zeroed_time + timedelta(minutes=time_value)
    elif time_unit == 'h':
        adjusted_time = zeroed_time + timedelta(hours=time_value)
    elif time_unit == 'd':
        adjusted_time = zeroed_time + timedelta(days=time_value)
    else:
        raise ValueError('Invalid time unit, use "m", "h", or "d".')

    # Return the adjusted time as an ISO 8601 formatted string
    return adjusted_time.isoformat()

