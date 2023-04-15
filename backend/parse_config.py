import json

def get_all_config(config_path):
    with open(config_path) as json_file:
        data = json.load(json_file)
    return data