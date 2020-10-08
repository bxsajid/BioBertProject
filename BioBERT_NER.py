import json
import os
import re
import traceback

import requests


def query_raw(text, url='https://bern.korea.ac.kr/plain'):
    return requests.post(url, data={'sample_text': text}).json()


if __name__ == '__main__':
    with open('json_data.json', mode='r') as f:
        descriptions = json.load(f)

    description_filename = 'description/description.txt'
    description_next_index_filename = 'description_next_index.txt'
    description_skip_index_filename = 'description_skip_index.txt'
    mesh_ids_filename = 'mesh_ids.txt'

    # read next description index from file, if file exists
    description_start_index = 0
    if os.path.isfile(description_next_index_filename):
        content = open(description_next_index_filename, mode='r').read()
        description_start_index = int(content) if content.strip() and isinstance(int(content), int) else 0

    SIZE = 2
    ERROR_COUNT_LIMIT = 3
    error_count = 0
    description_len = len(descriptions)

    for file_counter, i in enumerate(range(description_start_index, description_len, SIZE)):
        # write next description index to file
        open(description_next_index_filename, mode='w').write(str(i + SIZE))

        description = ' '.join(descriptions[i:i + SIZE])
        description = re.sub('\\s+', ' ', description)  # remove whitespace chars
        description = re.sub('"', '\'', description)  # replace " with '

        open(description_filename, mode='w', encoding='utf-8').write(description)
        file_size = os.stat(description_filename).st_size
        print(f'parsing description [{i}:{i + SIZE} of {description_len}], sizes: {[round(len(descriptions[j]) / 1024, 2) for j in range(i, i + SIZE)]}, total: {(file_size / 1024):.2f} KB')

        try:
            response = query_raw(description)
        except Exception as e:
            traceback.print_exc()

            # keep record of descriptions which has error
            open(description_skip_index_filename, mode='a').write(f'{i}:{i + SIZE}\n')

            error_count += 1

            # stop script on ERROR_COUNT_LIMIT successive error response
            if error_count == ERROR_COUNT_LIMIT:
                # remove temporary description file
                if os.path.isfile(description_filename):
                    os.remove(description_filename)
                break
            continue

        # reset error_count on success response
        error_count = 0

        # extract MESH id from BERN server response
        for denotation in response['denotations']:
            for id in denotation['id']:
                if id.startswith('MESH'):
                    mesh_id = id.lstrip('MESH:')
                    open(mesh_ids_filename, mode='a').write(f'{mesh_id}\n')

    # remove temporary description file
    if os.path.isfile(description_filename):
        os.remove(description_filename)
