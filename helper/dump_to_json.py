import json


def dump_to_json(json_data, filename):
    data = json.dumps(json_data)
    with open(filename, 'w+') as f:
        f.write(data)
