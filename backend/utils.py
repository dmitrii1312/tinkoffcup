import json
import re
from datetime import timedelta
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
