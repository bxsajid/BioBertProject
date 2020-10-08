import json
import re
import os
import traceback

import requests


def query_raw(text, url='https://bern.korea.ac.kr/plain'):
    return requests.post(url, data={'sample_text': text}).json()


def dump_to_json(json_data, filename):
    data = json.dumps(json_data)
    with open(filename, 'w') as f:
        f.write(data)


if __name__ == '__main__':
    with open('json_data.json', 'r') as f:
        descriptions = json.load(f)

    SIZE = 2
    mesh_ids = []
    error_descriptions = []
    error_count = 0
    description_len = len(descriptions)

    for file_counter, i in enumerate(range(0, description_len, SIZE)):
        description = ' '.join(descriptions[i:i + SIZE])
        description = re.sub('\\s+', ' ', description)  # remove whitespace chars
        description = re.sub('"', '\'', description)  # replace " with '

        open(f'description/description_{file_counter + 1}.txt', mode='w', encoding='utf-8').write(description)

        file_size = os.stat(f'description/description_{file_counter + 1}.txt').st_size
        print(f'parsing description [{i + 1}-{i + SIZE} of {description_len}], files: {[round(len(descriptions[j]) / 1024, 2) for j in range(i, i + SIZE)]}, total: {(file_size / 1024):.2f} KB')

        try:
            response = query_raw(description)
        except Exception as e:
            traceback.print_exc()
            error_descriptions.append(description)
            error_count += 1
            if error_count == 3:
                break
            continue

        for denotation in response['denotations']:
            for id in denotation['id']:
                if id.startswith('MESH'):
                    mesh_id = id.lstrip('MESH:')
                    mesh_ids.append(mesh_id)

    # remove duplicate MESH ids
    mesh_ids = list(set(mesh_ids))

    dump_to_json(mesh_ids, 'mesh_ids.json')
    dump_to_json(error_descriptions, 'error_descriptions.json')
