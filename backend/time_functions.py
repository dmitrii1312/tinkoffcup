import re
from datetime import timedelta


def parse_timedelta(s):
    match = re.match(r'(\d+)([msh])', s)
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
